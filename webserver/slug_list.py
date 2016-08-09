class SlugList:
    def __init__(self, digas_id, *slug):
        """Class representing a linked list of slugs in which the last slug
        points to a digas_id."""
        self.digas_id = digas_id
        self.slugs = list(slug)

    @classmethod
    def from_id(cls, digas_id):
        pass

    @classmethod
    def from_slug(cls, slug):
        pass

    @property
    def canonical_slug(self):
        return self.slugs[-1]

    @canonical_slug.setter
    def canonical_slug(self, new_slug):
        self.append(new_slug)

    def persist(self):
        pass

    def commit(self):
        pass

    def abort(self):
        pass

    def close(self):
        pass

    def append(self, new_slug):
        pass

    def optimize(self):
        pass

    @classmethod
    def is_in_use(cls, slug):
        pass

    @classmethod
    def _get_cursor(cls):
        pass

