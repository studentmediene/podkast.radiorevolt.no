from cached_property import threaded_cached_property as cached_property

from .. import ShowMetadataSource


class RadioRevolt_no(ShowMetadataSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @cached_property
    def _metadata_by_show_name(self):
        data = self._fetch_shows()
        shows = dict()
        for show in data:
            digas_id = show['digasId']
            # Skip all shows with no associated digasID
            if digas_id is not None:
                shows[digas_id] = show
        return shows

    def _fetch_shows(self):
        r = self.requests.get(
            self.settings['API_URL'] + "/shows",
        )
        r.raise_for_status()
        return r.json()

    def accepts(self, show):
        return super().accepts(show) and \
            show.id in self._metadata_by_show_name

    def populate(self, show):
        metadata = self._metadata_by_show_name[show.id]

        name = metadata['title']
        image = metadata['logoImageUrl']
        # This is not used, since RSS only allows one description
        short_description = metadata['lead']
        long_description = metadata['description']
        website = self.settings['SHOW_WEBSITE_TEMPLATE'] % metadata['slug']
        old = metadata['archived']
        language = metadata['language']
        explicit = metadata['explicitContent']

        show.name = name
        if image:
            show.image = image
        show.description = long_description
        show.website = website
        show.complete = old
        show.language = language
        show.explicit = explicit
