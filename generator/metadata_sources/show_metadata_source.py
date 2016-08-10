from abc import ABCMeta, abstractmethod


class ShowMetadataSource(metaclass=ABCMeta):
    """Class which provides metadata for a subset of all shows."""
    def __init__(self, settings, bypass, requests_session):
        """Initialize this show metadata source.

        The default implementation populates self.settings and self.bypass with values from the arguments.

        Args:
            settings (dict): Settings for this metadata source, taken from generator/settings.py.
            bypass (set): Set of show_ids (DigAS ID) which this metadata source should bypass (ie. not accept).
            requests_session: Requests session which will be used when making requests to other servers.
        """
        self.settings = settings
        """dict: Settings for this metadata source, taken from generator/settings.py."""
        self.bypass = bypass
        """set: Set of show_ids (DigAS ID) which this metadata source should bypass (that is, not accept)."""
        self.requests = requests_session
        """Requests session which shall be used when making requests to other servers."""

    @abstractmethod
    def accepts(self, show) -> bool:
        """Check if this metadata source has data for the given show.

        The default implementation checks if the show's show_id is present in the bypass-set.

        Args:
            show (Show): Check if there's metadata for this show.

        Returns:
            bool: True if this metadata source has metadata for the provided show, False otherwise.
        """
        return show.id not in self.bypass

    @abstractmethod
    def populate(self, show) -> None:
        """Populate the provided show with metadata.

        This method will set the different properties to values fetched from this metadata source.

        The default implementation does nothing.

        Args:
            show (Show): Show which will have its properties populated with metadata from this source.

        Returns:
            None

        Raises:
            SkipShow: When this episode shouldn't have its feed generated. Applicable only when feeds are batch
                generated; SkipShow is ignored when a show is requested explicitly (but it will still stop execution
                in the metadata source, so make your changes before raising SkipShow).
        """
        pass

    def prepare_batch(self) -> None:
        """Called to signal that information about all available shows should be downloaded.

        This method should download information about all shows, so that subsequent calls to
        accept and populate don't cause a network roundtrip. This is done to save time when
        generating all feeds.

        The default implementation does nothing.
        """
        pass
