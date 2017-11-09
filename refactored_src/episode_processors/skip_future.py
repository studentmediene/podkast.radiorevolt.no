from . import SkipEpisode, EpisodeProcessor
from datetime import datetime
from pytz import timezone
import pytz


class SkipFutureEpisodes(EpisodeProcessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def accepts(self, episode) -> bool:
        return super().accepts(episode)\
               and episode.publication_date > datetime.now(pytz.utc)

    def populate(self, episode) -> None:
        raise SkipEpisode
