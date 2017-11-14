from show_processors import ShowProcessor
from web_utils.local_image import LocalImage


class UseLocalImage(ShowProcessor):
    """
    Processor which puts LocalImage to use by changing the image URL.

    Settings: (none)
    """
    def accepts(self, show) -> bool:
        return super().accepts(show) and show.image

    def populate(self, show) -> None:
        show.image = LocalImage(show.image).get_image_url()
