from cached_property import threaded_cached_property as cached_property

from show_processors import ShowProcessor

ORIG_IMAGE_PREFIX = "http://dusken.no/media/thumbs/uploads/images/"
ORIG_IMAGE_SUFFIX = ".170x170_q85_crop_upscale.jpg"
NEW_IMAGE_PREFIX = "http://dusken.no/media/uploads/images/"
NEW_IMAGE_SUFFIX = ""


class Chimera(ShowProcessor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @cached_property
    def shows(self):
        r = self.requests.get(self.settings['api'] + "/shows/", params={"format": "json"})
        r.raise_for_status()
        json = r.json()
        return {show['showID']: show for show in json}

    def accepts(self, show) -> bool:
        return super().accepts(show) and show.id in self.shows

    def populate(self, show) -> None:
        metadata = self.shows[show.id]

        show.name = metadata['name']

        show.complete = metadata['is_old']

        show.description = metadata['lead']

        show.image = NEW_IMAGE_PREFIX + metadata['image'][len(ORIG_IMAGE_PREFIX):-len(ORIG_IMAGE_SUFFIX)] + \
                     NEW_IMAGE_SUFFIX

    def prepare_batch(self):
        _ = self.shows
