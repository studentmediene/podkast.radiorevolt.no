from podgen import Podcast


class Show(Podcast):
    """
    Data-oriented class for storing information about a show, as well as its
    episodes.
    """
    def __init__(
            self,
            name: str,
            id: int,
            **kwargs
    ):
        """Initialize a new show with the provided data.

        Args:
            name (str): Name of the show. Obligatory.
            id (int): DigAS ID for the show. Obligatory.
        """
        self.progress_i = 0
        self.progress_n = None

        super().__init__(**kwargs)
        self.name = name
        """Name of the show"""
        self.id = id
        """DigAS ID"""
