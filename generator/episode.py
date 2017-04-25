import podgen
import copy
from . import settings as SETTINGS


class Episode(podgen.Episode):
    """Class representing a single podcast episode."""

    def __init__(self, show=None, deprecated_url=None, **kwargs):
        self.show = show
        """The Show this Episode belongs to. Only used to identify which episode
        this is (and where to collect data for it)."""
        self.deprecated_url = deprecated_url
        """The previous URL used. Stored to enable searching for it in old
        metadata."""
        super().__init__(**kwargs)

    def set_defaults(self):
        if self.summary is None and self.long_summary is not None:
            # Use the first line in long description (or everything if there's no newline)
            first_newline = self.long_summary.find("\n")
            self.summary = self.long_summary[:first_newline] if first_newline != -1 else self.long_summary
        if self.id is None:
            self.id = self.media.url

    def rss_entry(self):
        self.set_defaults()

        if SETTINGS.URL_REDIRECTION_SOUND_URL and self.media:
            sound_url = SETTINGS.URL_REDIRECTION_SOUND_URL(self.media.url, self)
        else:
            sound_url = self.media.url

        if SETTINGS.URL_REDIRECTION_ARTICLE_URL and self.link:
            article_url = SETTINGS.URL_REDIRECTION_ARTICLE_URL(self.link, self)
        else:
            article_url = self.link

        # Temporary set media and link
        old_media = copy.copy(self.media)
        old_link = self.link

        self.media.url = sound_url
        self.link = article_url

        item = super().rss_entry()

        self.media = old_media
        self.link = old_link

        return item
