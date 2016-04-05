from .episode_metadata_source import EpisodeMetadataSource
from .show_metadata_source import ShowMetadataSource
# Import the metadata sources you will use here.
from .episode.skip_future import SkipFutureEpisodes

"""Metadata sources.

This module contains lists with metadata sources to be used, in the order they will be queried.
The order is important, since metadata from a later source will override metadata from an earlier one
(if they provide data for the same fields).

An episode metadata source must extend EpisodeMetadataSource, and likewise for show metadata sources which must extend
ShowMetadataSource.

Attributes:
    EPISODE_METADATA_SOURCES (list): List of episode metadata sources, in the order they will be executed
        (with the last one overriding data from the earlier ones).

    SHOW_METADATA_SOURCES (list): List of show metadata sources, in the order they will be executed
        (with the last one overriding data from the earlier ones).
"""


EPISODE_METADATA_SOURCES = [
    SkipFutureEpisodes,
]


SHOW_METADATA_SOURCES = [

]
