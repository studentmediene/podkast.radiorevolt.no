from cached_property import threaded_cached_property as cached_property

from . import ShowProcessor


class Kapina(ShowProcessor):
    """
    Class for fetching metadata from Kapina. Note that Kapina has very limited
    support for fetching data for podcasts, since there is NO information about
    how a show relates to the Digas database, and there is NO information about
    podcasts or podcast episodes in Kapina. The best we can do is hope the show
    names are equal.

    Settings:
        api: URL at which GraphQL can be queried.
        show_url_template: URL where a show can be found. %s is replaced by the
            show slug.
        image_template: URL where images are found. %s is replaced by the path
            returned from the Kapina backend.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        required_settings = [
            'api',
            'show_url_template',
            'image_template',
        ]
        missing_required_settings = list(
            filter(lambda s: s not in self.settings, required_settings)
        )
        if missing_required_settings:
            raise RuntimeError("Required settings for {class_} are missing: {settings!r}"
                               .format(class_=self.__class__.__name__, settings=missing_required_settings))


    @cached_property
    def _metadata_by_show_name(self):
        data = self._fetch_shows()
        show_list = data['data']['allShows']
        return {show['name'].lower(): show for show in show_list}

    def _fetch_shows(self):
        r = self.requests.get(
            self.settings['api'],
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
            show.name.lower() in self._metadata_by_show_name

    def populate(self, show):
        metadata = self._metadata_by_show_name[show.name.lower()]

        name = metadata['name']
        image = metadata['image']
        short_description = metadata['lead']
        long_description = metadata['content']
        website = self.settings['show_url_template'] % metadata['slug']
        old = metadata['archived']

        show.name = name
        if image:
            show.image = self.settings['image_template'] % image
        show.description = long_description
        show.website = website
        show.complete = old
