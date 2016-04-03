from abc import ABCMeta, abstractmethod


class EpisodeMetadataSource(metaclass=ABCMeta):
    """Class which provides metadata for a subset of all episodes."""
    @abstractmethod
    def __init__(self):
        """Initialize new episode metadata source."""
        pass

    @abstractmethod
    def accepts(self, episode) -> bool:
        """Check if this metadata source has metadata for the given episode.

        Args:
            episode (Episode): Episode which will be evaluated.

        Returns:
            bool: True if this metadata source has metadata for the provided episode, False otherwise.
        """
        pass

    @abstractmethod
    def populate(self, episode) -> None:
        """Populate the provided episode with metadata.

        This method will set the different properties to values fetched from this metadata source.

        Args:
            episode (Episode): Episode which will have its properties populated with new metadata.

        Returns:
            None
        """
        pass
