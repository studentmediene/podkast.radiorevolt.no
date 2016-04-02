import datetime
import requests
from feedgen.feed import FeedEntry, FeedGenerator
from . import settings as SETTINGS


class Episode:
    def __init__(self, sound_url, title, description, date: datetime.date, article_url=None, author=None,
                 author_email=None, long_description=None):
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

    def add_to(self, fg: FeedGenerator) -> FeedEntry:
        if self._feed_entry is None:
            fe = fg.add_entry()
            fe.id(self.sound_url)
            fe.guid(self.sound_url)
            fe.title(self.title)
            fe.content(self.description)
            fe.enclosure(self.sound_url)
            fe.author({'name': self.author, 'email': self.author_email})
            fe.link({'href': self.article_url})
            fe.published(self.date)

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
