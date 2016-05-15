import datetime
import requests
from feedgen.feed import FeedGenerator, FeedEntry
from . import settings as SETTINGS
import threading
import os
import json
from tinytag.tinytag import TinyTag
import tempfile
from cached_property import cached_property
import sqlite3

# Number of threads that can download episodes at the same time.
MAX_CONCURRENT_EPISODE_DOWNLOADS = 10
# Max size of memory that can be used by download process at any time.
max_megabytes = 500
# How many bytes shall be read into memory before they're written to disc?
CHUNK_SIZE = (max_megabytes // MAX_CONCURRENT_EPISODE_DOWNLOADS) * (1024 ** 2)


class Episode:
    """Class representing a single podcast episode."""
    # Create the required table(s) if they don't exist already.
    # (Do it here to ensure it's only done once)

    _create_table_durations = sqlite3.connect(SETTINGS.EPISODE_DURATIONS_DB)
    _create_table_durations.execute("create table if not exists durations (id text primary key, duration text)")
    _create_table_durations.close()

    _create_table_size = sqlite3.connect(SETTINGS.EPISODE_SIZES_DB)
    _create_table_size.execute("create table if not exists sizes (id text primary key, filesize integer)")
    _create_table_size.close()

    _download_constrain = threading.BoundedSemaphore(MAX_CONCURRENT_EPISODE_DOWNLOADS)

    def __init__(self, sound_url: str, title: str, show, date: datetime.datetime, requests_session: requests.Session,
                 article_url: str = None, author: str = None, author_email: str=None, short_description: str=None,
                 long_description: str = None, image: str = None, explicit: bool=None):
        """
        Initialize this episode with the given data.

        Args:
            sound_url (str): URL on which this episode MP3-file can be found. Mandatory.
            title (str): Name which will identify this episode to the end user. Mandatory.
            show (Show): The Show which this episode belongs to. Used by episode metadata sources. Mandatory.
            date (datetime.datetime): The timezone-aware date and time this episode was published. Mandatory.
            requests_session (requests.Session): Requests session which will be used when making requests to other
                servers. Mandatory.
            article_url (str): URL on which the entire description can be read, for example article on dusken.no.
                Defaults to sound_url.
            author (str): Name of the person who authored this episode. Defaults to the show's author.
            author_email (str): Email of the person who authored this episode. Defaults to the show's editorial email.
            short_description (str): Short description used to give users an idea on what this episode contains. Cannot
                contain markup of any kind. Defaults to the episode's title, or the first line of long_description if
                present.
            long_description (str): Long description shown when users hover over an (i) icon. Used to describe the episode
                more than the short_description can. HTML is supported and preferred; metadata sources must convert to
                HTML themselves. Defaults to short_description.
            image (str): URL to image for this episode. Must be between 1400x1400 and 3000x3000 pixels, and PNG or JPG.
                Defaults to using the feed's image.
            explicit (bool): True if this episode is inappropiate to children, False if it is appropiate, None to use
                the show's explicit value.
        """
        # Mandatory parameters
        self.sound_url = sound_url
        """str: URL on which this episode MP3-file can be found. Read-only."""

        self.title = title
        """str: Name which will identify this episode to the end user."""

        if short_description is not None:
            self.short_description = short_description
        elif long_description is not None:
            # Use the first line in long description (or everything if there's no newline)
            first_newline = long_description.find("\n")
            self.short_description = long_description[:first_newline] if first_newline != -1 else long_description
        else:
            # No description supplied; use title
            self.short_description = title
            """str: Short description used to give users an idea on what this episode contains. Cannot
        contain markup of any kind."""

        self.date = date
        """datetime.datetime: The timezone-aware date and time this episode was published."""

        self.show = show
        """Show: The Show which this episode belongs to. Used by episode metadata sources."""

        self.requests = requests_session
        """requests.Session: The Requests session which shall be used when making requests to other servers."""

        # Optional parameters
        self.article_url = article_url if article_url is not None else sound_url
        """str: URL on which the entire description can be read, for example article on dusken.no."""

        self.author = author if author is not None else show.author
        """str: Name of the person who authored this episode."""

        self.author_email = author_email if author_email is not None else show.editorial_email
        """str: Email of the person who authored this episode."""

        self.long_description = long_description if long_description is not None else short_description
        """str: Long description shown when users hover over an (i) icon. Used to describe the episode
    more than the short_description can. HTML is supported and preferred; metadata sources must convert to
    HTML themselves."""

        self.image = image
        """str: URL to image for this episode. Must be between 1400x1400 and 3000x3000 pixels, and PNG or JPG."""

        self.explicit = explicit
        """bool: True if this episode is inappropiate to children, False if it is appropiate, None to use show's
        explicit value."""

        # Internal properties
        self.__size = None
        self._feed_entry = None

    @cached_property
    def size(self) -> int:
        """Number of bytes this episode is. Read-only."""
        db = None
        try:
            # Create new database connection (a new one each time, since it is bound to one thread)
            db = sqlite3.connect(SETTINGS.EPISODE_SIZES_DB)
            db.execute("PRAGMA busy_timeout = 30000")
            # Try to fetch this episode's filesize
            c = db.execute("SELECT filesize FROM sizes WHERE id=?", (self.sound_url,))
            value = c.fetchone()
            c.close()
            # Did we get it?
            if value:
                return str(value[0])
            else:
                # Nope, calculate and save it for later times
                size = self._get_size()
                db.execute("INSERT INTO sizes (id, filesize) VALUES (:id, :filesize)",
                           {"id": self.sound_url, "filesize": size})
                db.commit()
                return size
        finally:
            if db:
                db.close()

    def _get_size(self) -> int:
        head = self.requests.head(self.sound_url, allow_redirects=True)
        return head.headers['content-length']

    @property
    def duration(self) -> str:
        """String representing how long this episodes lasts, in format HH:MM:SS. None if not available. Read-only."""
        db = None
        try:
            # Create new database connection (we do it here because a connection can only be used in the thread it's
            # created in).
            db = sqlite3.connect(SETTINGS.EPISODE_DURATIONS_DB)
            db.execute("PRAGMA busy_timeout = 30000")
            # Fetch any saved duration, if it exists
            c = db.execute("SELECT duration FROM durations WHERE id=?", (self.sound_url,))
            value = c.fetchone()
            c.close()

            # Was there a duration saved for this episode?
            if value:
                # Yes, use it
                return value[0]
            else:
                return None
        finally:
            if db:
                db.close()

    def calculate_duration(self, force: bool =False) -> bool:
        """
        Find the episode's duration and save it in the database.

        Args:
            force (bool): Set to True to force a re-download and re-evaluation of the episode's duration.

        Returns:
            bool: True if the duration was updated, False if it was not.
        """
        update = False
        if self.duration is not None:
            if not force:
                return False
            else:
                update = True
        db = sqlite3.connect(SETTINGS.EPISODE_DURATIONS_DB)
        db.execute("PRAGMA busy_timeout = 30000")
        try:

            duration = self._fetch_duration()
            if duration is None:
                return False
            # Convert to string conforming to iTunes' format
            hours = (duration.days * 24) + (duration.seconds // (60 * 60))
            minutes = (duration.seconds % (60 * 60)) // 60
            seconds = duration.seconds % 60
            duration_string = "{hours:02d}:{minutes:02d}:{seconds:02d}" \
                .format(hours=hours, minutes=minutes, seconds=seconds)

            # Persist this string in the database
            if not update:
                try:
                    db.execute("INSERT INTO durations (id, duration) VALUES (:id, :duration)",
                               {"id": self.sound_url, "duration": duration_string})
                except sqlite3.IntegrityError:
                    # There is already an entry for this episode -
                    # someone else has found the duration while we were busy, so just update it
                    update = True
            if update:
                db.execute("UPDATE durations SET duration=:duration WHERE id=:id",
                           {"id": self.sound_url, "duration": duration_string})

            db.commit()
            return True
        finally:
            if db:
                db.close()

    def _fetch_duration(self) -> datetime.timedelta:
        """Download episode and find its duration."""

        while not self._download_constrain.acquire(timeout=10):
            if SETTINGS.CANCEL.is_set():
                return None
        try:
            if SETTINGS.CANCEL.is_set():
                return None
            # Start fetching mp3 file
            r = self.requests.get(self.sound_url, stream=True)
            # Save the mp3 file (streaming it so we won't run out of memory)
            filename = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fd:
                    filename = fd.name
                    for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                        fd.write(chunk)
                        del chunk
                        if SETTINGS.CANCEL.is_set():
                            return None
                # Read its metadata and determine duration
                tag = TinyTag.get(filename)
                return datetime.timedelta(seconds=tag.duration)
            finally:
                # Remove temporary file
                try:
                    if filename:
                        os.remove(filename)
                except FileNotFoundError:
                    pass
        finally:
            self._download_constrain.release()

    def add_to_feed(self, fg: FeedGenerator) -> FeedEntry:
        """Add this episode to the given feed, but don't fill in any details yet.

        Args:
            fg (FeedGenerator): The feed which this episode is to be added to.

        Returns:
            FeedEntry: The new FeedEntry.

        Raises:
            RuntimeError: if invoked after this episode has already been added to a feed.
    """
        if self._feed_entry is None:
            fe = fg.add_entry()

            self._feed_entry = fe
            return fe
        else:
            raise RuntimeError("This episode is already added to a FeedGenerator")

    def populate_feed_entry(self):
        """Write data to the FeedEntry associated with this episode.

        You will need to call add_to_feed first."""
        if self._feed_entry is None:
            raise RuntimeError("populate_feed_entry was called before this episode was added to a feed.")

        if SETTINGS.URL_REDIRECTION_SOUND_URL:
            sound_url = SETTINGS.URL_REDIRECTION_SOUND_URL(self.sound_url, self)
        else:
            sound_url = self.sound_url

        if SETTINGS.URL_REDIRECTION_ARTICLE_URL:
            article_url = SETTINGS.URL_REDIRECTION_ARTICLE_URL(self.article_url, self)
        else:
            article_url = self.article_url

        fe = self._feed_entry
        fe.id(self.sound_url)
        fe.guid(self.sound_url)  # Don't use URL redirection service for GUID
        fe.title(self.title)
        fe.description(self.short_description)
        fe.content(self.long_description, type="CDATA")
        fe.enclosure(sound_url, self.size, "audio/mpeg")
        fe.author({'name': self.author, 'email': self.author_email})
        fe.link({'href': article_url})
        fe.published(self.date)

        duration = self.duration
        if duration is not None:
            fe.podcast.itunes_duration(duration)

        if self.image is not None:
            fe.podcast.itunes_image(self.image)

        if self.explicit is not None:
            fe.podcast.itunes_explicit(self.explicit)

    def remove_from_feed(self, fg: FeedGenerator) -> None:
        """Remove this episode from the given feed."""
        if self._feed_entry is not None:
            fg.remove_entry(self._feed_entry)
            self._feed_entry = None
        else:
            raise RuntimeError("This episode is not yet added to any FeedGenerator")
