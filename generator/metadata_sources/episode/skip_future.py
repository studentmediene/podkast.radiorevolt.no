from .. import SkipEpisode, EpisodeMetadataSource
from datetime import datetime
from pytz import timezone
import pytz


class SkipFutureEpisodes(EpisodeMetadataSource):
    def __init__(self):
        EpisodeMetadataSource.__init__(self)

    def accepts(self, episode) -> bool:
        return episode.date > datetime.now(pytz.utc)

    def populate(self, episode) -> None:
        raise SkipEpisode
