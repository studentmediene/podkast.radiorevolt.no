from . import settings as SETTINGS
from .episode_source import EpisodeSource
from feedgen.feed import FeedGenerator


class Show:
    def __init__(
            self,
            title: str,
            short_description: str =None,
            image: str =None,
            category: list =None,
            language: str ="no",
            show_url: str =None,
            editorial_email: str =None,
            technical_email: str =None,
            copyright_: str =None,
            old: bool =False,
            long_description: str =None,
            author: str =None,
            explicit: bool =None,
    ):
        self.title = title

        self.short_description = short_description if short_description is not None \
            else SETTINGS.DEFAULT_SHORT_FEED_DESCRIPTION
        self.long_description = long_description if long_description is not None else short_description
        self.image = image
        self.category = category
        self.language = language
        self.show_url = show_url
        self.editorial_email = editorial_email if editorial_email is not None else SETTINGS.DEFAULT_EDITORIAL_EMAIL
        self.technical_email = technical_email if technical_email is not None else SETTINGS.DEFAULT_TECHNICAL_EMAIL
        self.copyright = copyright_
        self.old = old
        self.author = author if author is not None else title
        self.explicit = explicit

        self.feed = None

    def init_feed(self) -> FeedGenerator:
        feed = FeedGenerator()
        feed.load_extension('podcast', rss=True)

        feed.title(self.title)

        feed.podcast.itunes_subtitle(self.short_description)
        feed.podcast.itunes_summary(self.long_description)
        if self.image is not None:
            feed.podcast.itunes_image(self.image)
        if self.category is not None:
            feed.podcast.itunes_category(self.category)
        feed.podcast.itunes_language(self.language)
        feed.podcast.itunes_link(self.show_url)
        feed.managingEditor(self.editorial_email)
        feed.webMaster(self.technical_email)
        if self.copyright is not None:
            feed.rights(self.copyright)
        feed.podcast.itunes_complete(self.old)
        feed.podcast.itunes_author(self.author)
        if self.explicit is not None:
            feed.podcast.itunes_explicit(self.explicit)

        self.feed = feed

        return feed

    def add_episodes(self, episode_source: EpisodeSource, metadata_sources: list):
        for episode in episode_source.episode_generator():
            # Find out what source, if any, accepts this episode
            selected_source = None
            for source in metadata_sources:
                if source.accepts(episode):
                    selected_source = source
                    break
            # Did any source accept the episode?
            if selected_source is not None:
                # Yes, use it
                selected_source.populate(episode)
            # Populate feed with this episode
            episode.add_to(self.feed)
