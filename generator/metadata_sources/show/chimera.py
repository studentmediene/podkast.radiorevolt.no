from .. import ShowMetadataSource
from ...settings import METADATA_SOURCE
import requests
from cached_property import cached_property

SETTINGS = METADATA_SOURCE['CHIMERA']

ORIG_IMAGE_PREFIX = "http://dusken.no/media/thumbs/uploads/images/"
ORIG_IMAGE_SUFFIX = ".170x170_q85_crop_upscale.jpg"
NEW_IMAGE_PREFIX = "http://dusken.no/media/uploads/images/"
NEW_IMAGE_SUFFIX = ""


class Chimera(ShowMetadataSource):

    def __init__(self):
        ShowMetadataSource.__init__(self)

    @cached_property
    def shows(self):
        r = requests.get(SETTINGS['API_URL'] + "/shows/", params={"format": "json"})
        r.raise_for_status()
        json = r.json()
        return {show['showID']: show for show in json}

    def accepts(self, show) -> bool:
        return show.show_id in self.shows

    def populate(self, show) -> None:
        metadata = self.shows[show.show_id]

        show.title = metadata['name']

        show.old = metadata['is_old']

        show.short_description = metadata['lead']

        show.long_description = metadata['description']

        show.image = NEW_IMAGE_PREFIX + metadata['image'][len(ORIG_IMAGE_PREFIX):-len(ORIG_IMAGE_SUFFIX)] + \
                     NEW_IMAGE_SUFFIX