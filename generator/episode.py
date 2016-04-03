import datetime
import requests
from feedgen.feed import FeedGenerator, FeedEntry
from . import settings as SETTINGS
import threading
import os
import json
from tinytag.tinytag import TinyTag


class Episode:
    duration_file_lock = threading.RLock()
    duration_file_name = os.path.join(os.path.dirname(__file__), "episode_durations.txt")
    durations = None
    temp_file_id = 0
    temp_file_lock = threading.RLock()

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

    def __init__(self, sound_url, title, description, date: datetime.date, article_url=None, author=None,
                 author_email=None, long_description=None, image=None):
        # Mandatory parameters
        self.sound_url = sound_url
        self.title = title
        self.description = description
        self.date = date

        # Optional parameters
        self.article_url = article_url if article_url is not None else sound_url
        self.author = author if author is not None else SETTINGS.DEFAULT_AUTHOR
        self.author_email = author_email if author_email is not None else SETTINGS.DEFAULT_AUTHOR_EMAIL
        self.long_description = long_description if long_description is not None else description
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
    def duration(self) -> datetime.timedelta:
        with self.duration_file_lock:
            # Check if we've loaded durations from file
            if self.durations is None:
                # Not yet, try to load from file
                try:
                    self.load_durations()
                except FileNotFoundError:
                    # Create empty file so we can load from it later
                    self.durations = dict()
                    self.save_durations()
        # Check if there's an entry for this file now that self.durations is a dict
        if self.sound_url in self.durations.keys():
            return self.durations[self.sound_url]
        else:
            # Find and save the duration for this episode
            duration = self.get_duration()
            with self.duration_file_lock:
                self.durations[self.sound_url] = duration
                self.save_durations()
            return duration

    @property
    def duration_string(self) -> str:
        return str(self.duration)

    def get_duration(self) -> datetime.timedelta:
        # Start fetching mp3 file
        r = requests.get(self.sound_url, stream=True)
        # Find unique filename for mp3 file (it must be downloaded so it can be opened by TinyTag)
        filename = str(self.get_temp_id()) + ".temporary.mp3"
        # Save the mp3 file (streaming it so we won't run out of memory)
        try:
            with open(filename, 'wb') as fd:
                # TODO: Find a reasonable chunk size
                for chunk in r.iter_content(chunk_size=4096):
                    fd.write(chunk)

            # Read its metadata and determine duration
            tag = TinyTag.get(filename)
            return datetime.timedelta(seconds=tag.duration)
        finally:
            # Remove temporary file
            try:
                os.remove(filename)
            except FileNotFoundError:
                pass

    def add_to(self, fg: FeedGenerator) -> FeedEntry:
        if self._feed_entry is None:
            fe = fg.add_entry()
            fe.id(self.sound_url)
            fe.guid(self.sound_url)
            fe.title(self.title)
            fe.content(self.description)
            fe.enclosure(self.sound_url, self.size, "audio/mpeg")
            fe.author({'name': self.author, 'email': self.author_email})
            fe.link({'href': self.article_url})
            fe.published(self.date)

            fe.itunes_duration(self.duration_string)

            if self.image is not None:
                fe.itunes_image(self.image)

            self._feed_entry = fe
            return fe
        else:
            raise RuntimeError("This episode is already added to a FeedGenerator")

    def remove_from(self, fg: FeedGenerator) -> None:
        if self._feed_entry is not None:
            fg.remove_entry(self._feed_entry)
            self._feed_entry = None
        else:
            raise RuntimeError("This episode is not yet added to any FeedGenerator")
