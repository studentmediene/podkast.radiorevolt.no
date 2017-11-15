from datetime import datetime

import pytz

from episode_processors import SkipEpisode, EpisodeProcessor


class SkipFutureEpisodes(EpisodeProcessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def accepts(self, episode) -> bool:
        return super().accepts(episode)\
               and episode.publication_date > datetime.now(pytz.utc)

    def populate(self, episode) -> None:
        raise SkipEpisode
