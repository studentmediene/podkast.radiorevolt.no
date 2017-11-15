import psycopg2.extensions

from .no_such_slug import NoSuchSlug
from .slug_already_in_use import SlugAlreadyInUse


class SlugList:
    def __init__(self, digas_id, *slug, connection, last_modified=None):
        """Class representing a linked list of slugs in which the last slug
        is the canonical slug, which points to a digas_id.

        Example:
            good-food → best-food → happy-food → 2015

        In this example, if the user accesses /good-food, s/he will be
        redirected to /happy-food. There, s/he will be served the feed for the
        show with Digas ID 2015.

        Note that the linked list is just a metaphor. In the database, all slugs
        are stored in slug_to_slug. They point to a record in slug_to_id, which
        is the canonical slug with the corresponding Digas ID. The canonical
        slug is also stored in slug_to_slug. This way, we need not perform
        recursive search to get the canonical slug. By using SQL's ON UPDATE
        CASCADE, all slugs will point to the new canonical slug when the slug
        field is changed in slug_to_id.

        This class assumes that you'll either (1) insert a new SlugList to the
        database, or (2) update an existing SlugList, never both in the same
        transaction. Therefore, when you create a new SlugList from scratch (by
        using the constructor directly), you can only populate digas_id and
        slugs, and call persist and then commit or abort. Likewise, you cannot
        change digas_id or slugs or call persist once the SlugList has been
        inserted into the database.

        Note that there is a real chance that your transaction will be rolled
        back because someone else already has done the same (race-condition).

        Slug is a term that refers to a human-readable part of the URL, usually
        used to identify an article. In our case, it identifies a show. In the
        URL http://podcast.example.com/nerdtalk, nerdtalk is the slug.
        """
        self.digas_id = digas_id
        self.slugs = list(slug)
        self.last_modified = last_modified
        self.connection = connection

    @classmethod
    def from_id(cls, digas_id: int, connection):
        """Return the SlugList that points to the given digas_id.

        Args:
            digas_id (int): The Digas ID which the SlugList shall match.
            connection (psycopg2.extensions.connection): Connection to use.
                The connection will be closed when you call commit or abort on
                the resulting SlugList.

        Returns:
            SlugList: The SlugList that points to the given digas_id.
        """
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT slug FROM slug_to_id WHERE digas_id = %s;",
                (digas_id,)
            )
            if not cursor.rowcount:
                raise NoSuchSlug("with digas_id = %s" % digas_id)
            row = cursor.fetchone()
            slug = row[0]

        return cls.from_slug(slug, connection)

    @classmethod
    def from_slug(cls, slug: str, connection):
        """
        Return the SlugList that slug is a part of.

        Args:
            slug (str): The slug that the SlugList shall match.
            connection (psycopg2.extensions.connection): Connection to use. A
                new will be created if this is not given. The connection will
                be closed when you call commit or abort on the resulting
                SlugList.

        Returns:
            SlugList: The SlugList which contains the given slug.
        """
        # First, find the canonical slug
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT canonical_slug FROM slug_to_slug WHERE slug = %s",
                (slug,)
            )
            row = cursor.fetchone()
            if row is None:
                raise NoSuchSlug(slug)
            canonical_slug = row[0]

        # Then, find all the other slugs
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT slug FROM slug_to_slug "
                "WHERE canonical_slug = %(canonical_slug)s "
                "AND NOT slug = %(canonical_slug)s",
                {"canonical_slug": canonical_slug}
            )
            if cursor.rowcount > 0:
                # Ensure the canonical slug is last
                slugs = [row[0] for row in cursor.fetchall()] + [canonical_slug]
            else:
                slugs = [canonical_slug]

        # Finally, find the digas_id
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT digas_id, last_modified FROM slug_to_id WHERE slug = %s",
                (canonical_slug,)
            )
            row = cursor.fetchone()
            digas_id = row[0]
            last_modified = row[1]

            # Create a new instance of this class, with the data fetched from the db
            return cls(digas_id, *slugs, last_modified=last_modified,
                       connection=connection)

    @property
    def canonical_slug(self):
        """
        The canonical slug that should be used instead of any other slug
        contained in this SlugList.

        You may assign a new value to this to change the canonical slug. The old
        canonical slug will still be in the list; your new value will just be
        appended. You'll need to commit() your changes for them to persist.
        """
        return self.slugs[-1]

    @canonical_slug.setter
    def canonical_slug(self, new_slug):
        self.append(new_slug)

    def persist(self):
        """Insert this SlugList into the database. This can only be called when
        creating a new SlugList. You are not allowed to change the name of slugs
        after the fact."""
        # First, insert the canonical slug and its mapping to Digas ID
        with self._create_cursor() as cursor:
            cursor.execute(
                "INSERT INTO slug_to_id (slug, digas_id) "
                "VALUES (%s, %s)",
                (self.canonical_slug, self.digas_id)
            )
        # Lastly, insert all slugs
        with self._create_cursor() as cursor:
            cursor.executemany(
                "INSERT INTO slug_to_slug (slug, canonical_slug) "
                "VALUES (%s, %s)",
                [(slug, self.canonical_slug) for slug in self.slugs]
            )

    def commit(self):
        """Indicate that you are done using this instance, and you'd like to
        persist the changes you've made through append, canonical_slug and
        persist.

        This will also close the underlying database connection.
        """
        try:
            self.connection.commit()
        finally:
            self.connection.close()

    def abort(self):
        """Indicate that you are done using this instance, and you'd like to
        rollback the changes you've made through append, canonical_slug and
        persist.

        This will also close the underlying database connection.
        """
        try:
            self.connection.rollback()
        finally:
            self.connection.close()

    def append(self, new_slug: str):
        """
        Add new_slug to the end of this SlugList. new_slug becomes the new
        canonical slug which all other slugs will point to.

        Can only be called on a SlugList which has been inserted into the
        database.

        Args:
            new_slug (str): New slug to be added to the end of this SlugList.

        Raises:
            SlugAlreadyInUse: If another SlugList already contains the given
                slug.
        """
        already_in_list = new_slug in self.slugs

        # Is this slug in use elsewhere?
        with self._create_cursor() as cursor:
            cursor.execute(
                "SELECT canonical_slug FROM slug_to_slug WHERE slug = %s;",
                (new_slug,)
            )
            if cursor.rowcount and not already_in_list:
                canonical_slug = cursor.fetchone()[0]

                raise SlugAlreadyInUse(new_slug + " (canonical slug: " +
                                       (canonical_slug or new_slug) + ")")

        # Rename the current canonical slug to the new slug.
        # This update will cascade to all slugs.
        old_canonical_slug = self.canonical_slug
        with self._create_cursor() as cursor:
            cursor.execute(
                """
                UPDATE slug_to_id
                SET slug = %(new_slug)s
                WHERE slug = %(old_slug)s;
                """,
                {'new_slug': new_slug, 'old_slug': old_canonical_slug}
            )
            if not cursor.rowcount:
                raise RuntimeError("No row matched by update (%s)" %
                                   cursor.query)

        # Make sure the new slug is in slug_to_slug
        if not already_in_list:
            with self._create_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO slug_to_slug
                        (slug, canonical_slug)
                    VALUES
                        (%(new_slug)s, %(new_slug)s);
                    """,
                    {'new_slug': new_slug}
                )
                if not cursor.rowcount:
                    raise RuntimeError("No row matched by insert (%s)" %
                                       cursor.query)
        # If we got here, we are successful.
        self.slugs.append(new_slug)

    def prepend(self, new_slug: str):
        """
        Add new_slug before canonical_slug, thus making it redirect to this
        list's canonical slug. This can be used to add another alias for the
        canonical slug.

        Can only be called on a SlugList which has been inserted into the
        database.

        Args:
            new_slug (str): Slug which shall redirect to canonical_slug.

        Raises:
            SlugAlreadyInUse: If the slug is already in use by another list.
                You will need to start the transaction over if this occurs,
                by calling abort() and creating the SlugList anew.
        """
        if new_slug in self.slugs:
            # Our job here is done
            return

        try:
            with self._create_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO slug_to_slug
                      (slug, canonical_slug)
                    VALUES
                      (%(new_slug)s, %(can_slug)s);
                    """,
                    {'new_slug': new_slug, 'can_slug': self.canonical_slug}
                )
                if not cursor.rowcount:
                    raise RuntimeError("Query did not insert anything (%s)" %
                                       cursor.query)
        except psycopg2.IntegrityError as e:
            raise SlugAlreadyInUse(new_slug) from e
        # We were successful
        self.slugs.insert(-1, new_slug)

    def _create_cursor(self) -> psycopg2.extensions.cursor:
        """
        Create and return a Cursor, using this instance's connection.

        Returns:
            psycopg2.extensions.cursor: Cursor connected to the database using
                this instance's connection.
        """
        return self.connection.cursor()

    @classmethod
    def init_db(cls, connection):
        """
        Initialize the database, by creating the necessary tables and such.

        Needs only to be run once, when setting up podcast-feed-gen.

        You may pass a separate connection, so you can use different credentials
        than what's in settings.py. You might want to limit the usual user's
        permissions, after all.

        Args:
            connection (psycopg2.extensions.connection): The connection to use.
                A new connection using the parameters in settings.py will be
                created if this is not supplied.
        """
        connection.autocommit = True
        with connection.cursor() as cursor:
            create_table_query =\
"""-- Function which will automatically update a SlugList's last_modified datetime
CREATE FUNCTION update_last_modified_function()
RETURNS TRIGGER
AS
$$
BEGIN
    NEW.last_modified = clock_timestamp();
    RETURN NEW;
END;
$$
language 'plpgsql';

-- Mapping between a canonical slug and its Digas ID
CREATE TABLE slug_to_id (
  slug VARCHAR(50) PRIMARY KEY,
  digas_id INT NOT NULL UNIQUE,
  last_modified TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT clock_timestamp()
);

-- Automatically update last_modified on update
CREATE TRIGGER last_modified_on_slug_to_id
BEFORE UPDATE
ON slug_to_id
FOR EACH ROW
EXECUTE PROCEDURE update_last_modified_function();

-- Table for linked list of slugs
CREATE TABLE slug_to_slug (
  slug VARCHAR(50) PRIMARY KEY,
  canonical_slug VARCHAR(50) NOT NULL REFERENCES slug_to_id(slug) ON DELETE
    RESTRICT ON UPDATE CASCADE
);
"""
            cursor.execute(create_table_query)
