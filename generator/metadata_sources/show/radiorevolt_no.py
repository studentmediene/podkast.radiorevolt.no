from cached_property import threaded_cached_property as cached_property

from .. import ShowMetadataSource


class RadioRevolt_no(ShowMetadataSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @cached_property
    def _metadata_by_digas_show_id(self):
        data = self._fetch_shows()
        show_list = data['data']['allShows']
        return {show['digasShowId']: show for show in show_list if
                show['digasShowId']}

    def _fetch_shows(self):
        r = self.requests.get(
            self.settings['API_URL'],
            params={"query": """
            {
              allShows {
                digasShowId,
                name,
                image,
                lead,
                content,
                slug,
                archived,
              }
            }
            """},
        )
        r.raise_for_status()
        return r.json()

    def accepts(self, show):
        return super().accepts(show) and \
            show.id in self._metadata_by_digas_show_id

    def populate(self, show):
        metadata = self._metadata_by_digas_show_id[show.id]

        name = metadata['name']
        image = metadata['image']
        short_description = metadata['lead']
        long_description = metadata['content']
        website = self.settings['SHOW_WEBSITE_TEMPLATE'] % metadata['slug']
        old = metadata['archived']

        show.name = name
        if image:
            show.image = image
        show.description = long_description
        show.website = website
        show.complete = old
