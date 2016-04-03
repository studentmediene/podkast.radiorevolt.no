import datetime
import requests
from feedgen.feed import FeedGenerator, FeedEntry
from . import settings as SETTINGS
import threading
import os
import json
import email.utils
from tinytag.tinytag import TinyTag
import sys

MAX_CONCURRENT_EPISODE_DOWNLOADS = 10
CHUNK_SIZE = 50 * (1024 ** 2)
# 5 MB, meaning CHUNK_SIZE*MAX_CONCURRENT_EPISODE_DOWNLOADS = 50 MB can be in memory in any moment


class Episode:
    duration_file_lock = threading.RLock()
    duration_file_name = os.path.join(os.path.dirname(__file__), "episode_durations.txt")
    durations = None

    temp_file_id = 0
    temp_file_lock = threading.RLock()

    download_constrain = threading.BoundedSemaphore(MAX_CONCURRENT_EPISODE_DOWNLOADS)

    @classmethod
    def load_durations(cls):
        with cls.duration_file_lock:
            with open(cls.duration_file_name) as fp:
                cls.durations = json.load(fp)

    @classmethod
    def save_durations(cls):
        with cls.duration_file_lock:
            with open(cls.duration_file_name, mode="w") as fp:
                json.dump(cls.durations, fp)

    @classmethod
    def get_temp_id(cls):
        with cls.temp_file_lock:
            cls.temp_file_id += 1
            return cls.temp_file_id

    def __init__(self, sound_url, title,  show, date: datetime.date, article_url=None, author=None,
                 author_email=None, short_description=None, long_description:str=None, image=None):
        # Mandatory parameters
        self.sound_url = sound_url
        self.title = title
        if short_description is not None:
            self.short_description = short_description
        elif long_description is not None:
            # Use the first line in long description (or everything if there's no newline)
            first_newline = long_description.find("\n")
            self.short_description = long_description[:first_newline] if first_newline != -1 else long_description
        else:
            # No description supplied; use title
            self.short_description = title
        self.date = date
        self.show = show

        # Optional parameters
        self.article_url = article_url if article_url is not None else sound_url
        self.author = author if author is not None else SETTINGS.DEFAULT_AUTHOR
        self.author_email = author_email if author_email is not None else SETTINGS.DEFAULT_AUTHOR_EMAIL
        self.long_description = long_description if long_description is not None else short_description
        self.image = image

        # Internal properties
        self.__size = None
        self._feed_entry = None

    @property
    def size(self) -> int:
        """Support lazy loading of episode size"""
        if self.__size is None:
            self.__size = self.get_size()
        return self.__size

    def get_size(self) -> int:
        head = requests.head(self.sound_url, allow_redirects=True)
        return head.headers['content-length']

    @property
    def duration(self) -> str:
        with self.duration_file_lock:
            # Check if we've loaded durations from file
            if self.durations is None:
                # Not yet, try to load from file
                try:
                    self.load_durations()
                except FileNotFoundError:
                    # Create empty file so we can load from it later
                    Episode.durations = dict()
                    self.save_durations()
        # Check if there's an entry for this file now that self.durations is a dict
        if self.sound_url in self.durations.keys():
            return self.durations[self.sound_url]
        else:
            # Nope, find and save the duration for this episode
            duration = self.get_duration()

            hours = (duration.days*24) + (duration.seconds // (60*60))
            minutes = (duration.seconds % (60*60)) // 60
            seconds = duration.seconds % 60
            duration_string = "{hours:02d}:{minutes:02d}:{seconds:02d}"\
                .format(hours=hours, minutes=minutes, seconds=seconds)

            with self.duration_file_lock:
                self.durations[self.sound_url] = duration_string
                self.save_durations()
            return duration_string

    @property
    def date_string(self) -> str:
        return email.utils.format_datetime(self.date)

    def get_duration(self) -> datetime.timedelta:
        with self.download_constrain:
            # Start fetching mp3 file
            r = requests.get(self.sound_url, stream=True)
            # Find unique filename for mp3 file (it must be downloaded so it can be opened by TinyTag)
            filename = str(self.get_temp_id()) + ".temporary.mp3"
            # Save the mp3 file (streaming it so we won't run out of memory)
            try:
                with open(filename, 'wb') as fd:
                    # TODO: Find a reasonable chunk size
                    for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                        fd.write(chunk)
                        del chunk

                # Read its metadata and determine duration
                tag = TinyTag.get(filename)
                return datetime.timedelta(seconds=tag.duration)
            finally:
                # Remove temporary file
                try:
                    os.remove(filename)
                except FileNotFoundError:
                    pass

    def add_to_feed(self, fg: FeedGenerator) -> FeedEntry:
        if self._feed_entry is None:
            fe = fg.add_entry()

            self._feed_entry = fe
            return fe
        else:
            raise RuntimeError("This episode is already added to a FeedGenerator")

    def populate_feed_entry(self):
        """Write data to the FeedEntry associated with this episode.

        You will need to call add_to first."""
        if self._feed_entry is None:
            raise RuntimeError("populate_feed_entry was called before this episode was added to a feed.")
        fe = self._feed_entry
        fe.id(self.sound_url)
        fe.guid(self.sound_url)
        fe.title(self.title)
        fe.description(self.short_description)
        fe.content(self.long_description, type="CDATA")
        fe.enclosure(self.sound_url, self.size, "audio/mpeg")
        fe.author({'name': self.author, 'email': self.author_email})
        fe.link({'href': self.article_url})
        fe.published(self.date)

        if SETTINGS.FIND_EPISODE_DURATIONS:
            print("Finding durations...", file=sys.stderr)
            fe.podcast.itunes_duration(self.duration)

        if self.image is not None:
            fe.podcast.itunes_image(self.image)

    def remove_from_feed(self, fg: FeedGenerator) -> None:
        if self._feed_entry is not None:
            fg.remove_entry(self._feed_entry)
            self._feed_entry = None
        else:
            raise RuntimeError("This episode is not yet added to any FeedGenerator")
