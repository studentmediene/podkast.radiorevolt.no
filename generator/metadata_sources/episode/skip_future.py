from .. import SkipEpisode, EpisodeMetadataSource
from datetime import datetime


class SkipFutureEpisodes(EpisodeMetadataSource):
    def __init__(self):
        EpisodeMetadataSource.__init__(self)

    def accepts(self, episode) -> bool:
        return episode.date > datetime.utcnow()

    def populate(self, episode) -> None:
        raise SkipEpisode
