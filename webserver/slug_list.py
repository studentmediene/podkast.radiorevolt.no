from .no_such_slug import NoSuchSlug
from .slug_already_in_use import SlugAlreadyInUse


class SlugList:
    def __init__(self, digas_id, *slug):
        """Class representing a linked list of slugs in which the last slug
        points to a digas_id.

        This class assumes that you'll either (1) insert a new SlugList to the
        database, or (2) update an existing SlugList, never both in the same
        transaction. Therefore, when you create a new SlugList from scratch (by
        using the constructor directly), you can only populate digas_id and
        slugs, and call persist and then commit or abort. Likewise, you cannot
        change digas_id or slugs or call persist once the SlugList has been
        inserted into the database.

        Note that there is a real chance that your transaction will be rolled
        back because someone else already has done the same (race-condition).
        """
        self.digas_id = digas_id
        self.slugs = list(slug)

    @classmethod
    def from_id(cls, digas_id: int):
        """Return the SlugList that points to the given digas_id.

        Args:
            digas_id (int): The Digas ID which the SlugList shall match.

        Returns:
            SlugList: The SlugList that points to the given digas_id.
        """
        pass

    @classmethod
    def from_slug(cls, slug: str):
        """
        Return the SlugList that slug is a part of.

        Args:
            slug (str): The slug that the SlugList shall match.

        Returns:
            SlugList: The SlugList which contains the given slug.
        """
        pass

    @property
    def canonical_slug(self):
        """
        The canonical slug that should be used instead of any other slug
        contained in this SlugList.
        """
        return self.slugs[-1]

    @canonical_slug.setter
    def canonical_slug(self, new_slug):
        self.append(new_slug)

    def persist(self):
        """Insert this SlugList into the database. This can only be called when
        creating a new SlugList. You are not allowed to change the name of slugs
        after the fact."""
        pass

    def commit(self):
        """Indicate that you are done using this instance, and you'd like to
        persist the changes you've made through append, canonical_slug and
        persist.

        This will also close the underlying database connection.
        """
        pass

    def abort(self):
        """Indicate that you are done using this instance, and you'd like to
        rollback the changes you've made through append, canonical_slug and
        persist.

        This will also close the underlying database connection.
        """
        pass

    def append(self, new_slug: str):
        """
        Add new_slug to the end of this SlugList.

        Can only be called on a SlugList which has been inserted into the
        database.

        Args:
            new_slug (str): New slug to be added to the end of this SlugList.

        Raises:
            SlugAlreadyInUse: If another SlugList already contains the given
                slug.
        """
        pass

    @classmethod
    def _get_cursor(cls):
        """
        Get a connection to the database.

        Returns:
            Cursor that is connected to the database.
        """
        pass

    @classmethod
    def init_db(cls):
        """
        Initialize the database, by creating the necessary tables and such.

        Needs only to be run once, when setting up podcast-feed-gen.
        """
        pass
