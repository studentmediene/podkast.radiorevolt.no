from . import EpisodeProcessor


class Testing(EpisodeProcessor):
    def __init__(self, settings, bypass, requests_session, *args, **kwargs):
        print(repr(settings))
        super().__init__(settings, bypass, requests_session, *args, **kwargs)

    def accepts(self, episode) -> bool:
        return True

    def populate(self, episode) -> None:
        episode.title = "Bæsj"
