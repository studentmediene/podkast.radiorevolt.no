from utils.date2dt import date2dt

from episode_processors import EpisodeProcessor, SkipEpisode
from feed_utils.episode import Episode


class SkipByDate(EpisodeProcessor):
    """
    Episode processor which skips episodes based on end date, but can be
    configured to use different dates for different shows (as opposed to
    SkipAll, which can only be configured with start and end dates for all
    episodes).

    Settings:
        default: YYYY-MM-DD; first date to _not_ skip for shows without their
            own setting.
        <Digas Show ID>: YYYY-MM-DD; first date to _not_ skip for the show with
            the given Digas Show ID. This is then used instead of default.
    """
    def accepts(self, episode: Episode) -> bool:
        if not super().accepts(episode):
            return False

        if episode.show.id in self.settings:
            end_date = self.settings[episode.show.id]
        else:
            end_date = self.settings['default']

        end_datetime = date2dt(end_date)
        return episode.publication_date < end_datetime

    def populate(self, episode) -> None:
        raise SkipEpisode("Skipped because it was accepted by SkipByDate")
