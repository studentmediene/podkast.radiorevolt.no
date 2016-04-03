from abc import ABCMeta, abstractmethod


class ShowMetadataSource(metaclass=ABCMeta):
    """Class which provides metadata for a subset of all shows."""
    @abstractmethod
    def __init__(self):
        """Initialize this show metadata source."""
        pass

    @abstractmethod
    def accepts(self, show) -> bool:
        """Check if this metadata source has data for the given show.

        Args:
            show (Show): Check if there's metadata for this show.

        Returns:
            bool: True if this metadata source has metadata for the provided show, False otherwise.
        """
        pass

    @abstractmethod
    def populate(self, show) -> None:
        """Populate the provided show with metadata.

        This method will set the different properties to values fetched from this metadata source.

        Args:
            show (Show): Show which will have its properties populated with metadata from this source.

        Returns:
            None
        """
        pass
