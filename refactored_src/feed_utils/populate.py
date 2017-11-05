import logging
import copy

from ..show_processors import SkipShow
from ..episode_processors import SkipEpisode


logger = logging.getLogger(__name__)


def prepare_processors_for_batch(processors):
    """Tell all given processors to prepare for batch populating.

    This should be done if we will generate more than one feed.
    """
    for processor in processors:
        processor.prepare_for_batch()


def run_show_pipeline(
        show,
        processor_list,
        mask_skip_show: bool=True
):
    """
    Populate show with metadata by running the given show pipeline.

    Each processor in the processor_list will add metadata to the show, if they
    wish to.

    Args:
        show: Instance of Show to populate with new metadata.
        processor_list: The pipeline, i.e. list of processors to apply to show.
        mask_skip_show: Set to True to mask SkipShow exceptions, or set to
            False to let such exceptions from processors bubble up to caller.

    Returns:
        Copy of show with metadata populated by the processors.

    Raises:
        SkipShow: When a processor determines this show should be skipped, and
            mask_skip_show was False.
    """
    # Leave original show untouched
    show = copy.deepcopy(show)
    for processor in processor_list:
        if processor.accepts(show):
            try:
                processor.populate(show)
            except SkipShow as e:
                if mask_skip_show:
                    logger.debug("Ignoring SkipShow", exc_info=True)
                else:
                    raise e
    return show


def run_episode_pipeline(
        episode_list,
        processor_list,
        mask_skip_episode: bool=False
):
    """
    Populate all episodes with metadata by running the given episode pipeline.

    Args:
        episode_list: List of Episode to populate with new metadata.
        processor_list: The pipeline, i.e. list of processors to apply to
            each episode in episode_list.
        mask_skip_episode: Set to True to mask SkipEpisode exceptions, or set
            to False to let such exceptions lead to the episode being excluded
            from the list returned.

    Returns:
        List of copies of episodes with metadata populated by the processors.
    """
    resulting_episode_list = []
    for episode in episode_list:
        try:
            resulting_episode_list.append(
                _run_episode_pipeline_on_single_episode(
                    episode,
                    processor_list,
                    mask_skip_episode
                )
            )
        except SkipEpisode:
            logger.debug(
                "Skipping episode named {name} (URL: {url!r})"
                .format(name=episode.title, url=episode.media.url),
                exc_info=True
            )
            # Not adding episode to list, thus skipping it
    return resulting_episode_list


def _run_episode_pipeline_on_single_episode(
        episode,
        processor_list,
        mask_skip_episode
):
    """
    Populate the given episode with metadata by running the episode pipeline.

    Args:
        episode: Instance of Episode to populate with new metadata.
        processor_list: The pipeline, i.e. list of processors to apply to
            episode.
        mask_skip_episode: True if SkipEpisode from processors should be
            ignored, False if such exceptions should bubble up to caller.

    Returns:
        Copy of episode with metadata populated by the processors.

    Raises:
        SkipEpisode: When mask_skip_episode is False, and a processor raises
            SkipEpisode when populating the episode (to indicate it should not
            be included in the feed).
    """
    # Leave original episode untouched
    episode = copy.deepcopy(episode)
    logger.debug(
        "Processing episode {episodename} (from {showname})"
            .format(episodename=episode.title, showname=episode.show.name)
    )
    for processor in processor_list:
        if processor.accepts(episode):
            try:
                processor.populate(episode)
            except SkipEpisode:
                if mask_skip_episode:
                    logger.debug("Ignoring SkipEpisode", exc_info=True)
                else:
                    raise

    return episode
