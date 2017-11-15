import psycopg2.extensions
from web_utils.slug_list import SlugList


class SlugListFactory:
    """Class for creating instances of SlugList.

    Abstracts away the process of creating new connections from settings.
    """

    def __init__(self, db_settings):
        self.db_settings = db_settings

    def create_connection(self) -> psycopg2.extensions.connection:
        """
        Create and return a connection to the database.

        The parameters in db_settings are used to determine host, port,
        database, user and password. The connection has its isolation level set
        to "Serializable".

        Returns:
            psycopg2.extensions.connection: Connection to the database.
        """
        conn = psycopg2.connect(
            **self.db_settings
        )
        conn.set_session(
            isolation_level=psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE
        )
        return conn

    def _with_connection(self, func):
        conn = self.create_connection()
        try:
            return func(conn)
        finally:
            conn.close()

    def _with_conn_close_on_exception(self, func):
        conn = self.create_connection()
        try:
            return func(conn)
        except:
            conn.close()
            raise

    def init_db(self):
        def handle_init_db(conn):
            return SlugList.init_db(conn)
        return self._with_connection(handle_init_db)

    def from_slug(self, slug: str, connection=None):
        def do_from_slug(conn):
            conn = connection or conn
            return SlugList.from_slug(slug, conn)
        return self._with_conn_close_on_exception(do_from_slug)

    def from_id(self, digas_id: int, connection=None):
        def do_from_id(conn):
            conn = connection or conn
            return SlugList.from_id(digas_id, conn)
        return self._with_conn_close_on_exception(do_from_id)

    def create(self, digas_id: int, *slug, last_modified=None, connection=None):
        return SlugList(
            digas_id,
            *slug,
            last_modified=last_modified,
            connection=connection or self.create_connection()
        )
