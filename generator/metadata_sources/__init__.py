from .episode_metadata_source import EpisodeMetadataSource
from .show_metadata_source import ShowMetadataSource
from .skip_episode import SkipEpisode
from .skip_show import SkipShow

# Import the metadata sources you will use here.
from .episode.skip_future import SkipFutureEpisodes
from .episode.chimera import Chimera as ChimeraEpisode
from .show.chimera import Chimera as ChimeraShow
from .show.manual_changes import ManualChanges as ManualChangesShow
from .episode.manual_changes import ManualChanges as ManualChangesEpisode
from .episode.radiorevolt_no import RadioRevolt_no as RadioRevolt_noEpisode
from .show.radiorevolt_no import RadioRevolt_no as RadioRevolt_noShow
from .show.default_image import SetDefaultImageURL

"""Metadata sources.

This module contains lists with metadata sources to be used, in the order they will be queried.
The order is important, since metadata from a later source will override metadata from an earlier one
(if they provide data for the same fields).

An episode metadata source should extend EpisodeMetadataSource, and likewise for show metadata sources which should
extend ShowMetadataSource.

Attributes:
    EPISODE_METADATA_SOURCES (list): List of episode metadata sources, in the order they will be executed
        (with the last one overriding data from the earlier ones).

    SHOW_METADATA_SOURCES (list): List of show metadata sources, in the order they will be executed
        (with the last one overriding data from the earlier ones).
"""


EPISODE_METADATA_SOURCES = [
    ChimeraEpisode,
    ManualChangesEpisode,
    RadioRevolt_noEpisode,
    SkipFutureEpisodes,
]


SHOW_METADATA_SOURCES = [
    ChimeraShow,
    ManualChangesShow,
    RadioRevolt_noShow,
    SetDefaultImageURL,
]
