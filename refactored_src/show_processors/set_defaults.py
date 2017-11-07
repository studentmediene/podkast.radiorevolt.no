from podgen import Category, Person

from . import ShowProcessor


__all__ = ["SetDefaults"]


class SetDefaults(ShowProcessor):
    def accepts(self, show) -> bool:
        return super().accepts(show)

    def populate(self, show) -> None:
        self._set_if_false(show, "description", self.settings['description'])
        self._set_if_false(show, "category", Category(**self.settings['category']))
        self._set_if_false(show, "language", self.settings['language'])
        self._set_if_false(show, "website", self.settings['website'])
        self._set_if_false(show, "authors", [Person(**author) for author in self.settings['authors']])
        self._set_if_false(show, "web_master", Person(**self.settings['web_master']))
        self._set_if_none(show, "explicit", self.settings['explicit'])
        self._set_if_false(show, "owner", Person(**self.settings['owner']))

        if show.owner:
            self._set_if_false(show, "copyright", show.owner.name)

    @staticmethod
    def _set_if_false(show, attribute, default_value):
        if (not getattr(show, attribute)) and default_value:
            setattr(show, attribute, default_value)

    @staticmethod
    def _set_if_none(show, attribute, default_value):
        if (getattr(show, attribute) is None) and (default_value is not None):
            setattr(show, attribute, default_value)
