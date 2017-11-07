from . import EpisodeProcessor


class Testing(EpisodeProcessor):
    def __init__(self, settings, bypass, requests_session, *args, **kwargs):
        super().__init__(settings, bypass, requests_session, *args, **kwargs)

    def accepts(self, episode) -> bool:
        return super().accepts(episode)

    def populate(self, episode) -> None:
        episode.title = "Bæsj"
