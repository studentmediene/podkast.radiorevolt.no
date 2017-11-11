from . import EpisodeProcessor


class RedirectorProcessor(EpisodeProcessor):
    """
    Class which applies Redirector to the episodes. Without this, the
    Redirector does nothing.

    In short, this will set the Episode's URL and link attributes so that they
    point to an intermediate URL hosted by this web application, so that
    downloads can be logged here rather than on the file server actually
    hosting the episodes. Therefore, this should usually be the very last
    episode processor, since other processors will rely on the Episode's URL
    to determine which metadata to apply.

    Settings: (none)
    """
    def accepts(self, episode) -> bool:
        return super().accepts(episode)

    def populate(self, episode) -> None:
        redirector = self.get_global('redirector')
        if episode.media.url:
            episode.media.url = \
                redirector.get_redirect_sound(episode.media.url, episode)
        if episode.link:
            episode.link = \
                redirector.get_redirect_article(episode.link, episode)
