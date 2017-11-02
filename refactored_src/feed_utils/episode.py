import podgen


class Episode(podgen.Episode):
    """Class representing a single podcast episode."""

    def __init__(self, show=None, deprecated_url=None, **kwargs):
        self.show = show
        """The Show this Episode belongs to. Only used to identify which episode
        this is (and where to collect data for it)."""
        self.deprecated_url = deprecated_url
        """The previous URL used. Stored to enable searching for it in old
        metadata."""
        super().__init__(**kwargs)
