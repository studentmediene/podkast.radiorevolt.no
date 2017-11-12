from podgen import Category, Person

from . import ShowProcessor


__all__ = ["SetDefaults"]


class SetDefaults(ShowProcessor):
    """
    Populate fields in the show which aren't populated yet, using the settings.

    Settings:
        description: Podcast description
        category:
          category: Main Itunes category
          subcategory: Sub Itunes category
        language: Podcast language
        website: Website podcast links to as its website
        authors:
          - name: Name of author
          - email: Email of author
          ...
        web_master:
          name: Name of web master
          email: Email of web master
        explicit: true/false, whether the podcast should not be played for kids
        owner:
          name: Name of owner
          email: Email of owner
        image: URL of podcast image to use.
    """
    def accepts(self, show) -> bool:
        return super().accepts(show)

    def populate(self, show) -> None:
        self._set_if_false(show, 'description', self.settings.get('description'))

        default_category = Category(**self.settings['category']) if self.settings.get('category') else None
        self._set_if_false(show, 'category', default_category)

        self._set_if_false(show, 'language', self.settings.get('language'))
        self._set_if_false(show, 'website', self.settings.get('website'))
        self._set_if_false(show, 'authors', [Person(**author) for author in self.settings['authors']] if self.settings.get('authors') else [])

        default_webmaster = Person(**self.settings['web_master']) if self.settings.get('web_master') else None
        self._set_if_false(show, 'web_master', default_webmaster)

        self._set_if_none(show, 'explicit', self.settings.get('explicit'))

        default_owner = Person(**self.settings['owner']) if self.settings.get('owner') else None
        self._set_if_false(show, 'owner', default_owner)

        if show.owner:
            self._set_if_false(show, 'copyright', show.owner.name)

        self._set_if_false(show, 'image', self.settings.get('image'))

    @staticmethod
    def _set_if_false(show, attribute, default_value):
        if (not getattr(show, attribute)) and default_value:
            setattr(show, attribute, default_value)

    @staticmethod
    def _set_if_none(show, attribute, default_value):
        if (getattr(show, attribute) is None) and (default_value is not None):
            setattr(show, attribute, default_value)
