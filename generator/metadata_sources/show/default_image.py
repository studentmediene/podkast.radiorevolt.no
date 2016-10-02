from .. import ShowMetadataSource
import warnings


class SetDefaultImageURL(ShowMetadataSource):
    """A metadata source for shows, which sets its image to a default if it's
    not set."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_default_image = 'IMAGE' in self.settings
        if not self.has_default_image:
            warnings.warn("SetDefaultImageURL is in use as a metadata source,"
                          " but there is no default image set in settings.py. "
                          "Key: IMAGE, value: absolute URL to the default "
                          "image.")

    def accepts(self, show) -> bool:
        return super().accepts(show) \
               and self.has_default_image \
               and not show.image

    def populate(self, show) -> None:
        show.image = self.settings['IMAGE']
