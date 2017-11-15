import sqlite3
import hashlib
import base64
import os.path
import urllib.parse


class Redirector:
    """Class responsible for translating between original URLs and our proxy
    redirect URLs, and back again."""
    def __init__(
            self,
            db_file,
            url_service,
            article_redirect_endpoint,
            sound_redirect_endpoint,
            url_for_func,
    ):
        """Create new instance of Redirector, used for translation between
        original URLs for sounds and articles, and our intermediate URLs. Used
        so we can log downloads on the server podcasts are served from.

        Args:
            db_file: Path to the sqlite3 database file used.
            url_service: Instance of UrlService, responsible for obtaining the
                canonical show slug for a show.
            article_redirect_endpoint: Name of function registered in Flask,
                which should be the target of redirects for articles. Must
                accept parameters show, the slug for the show; article, the
                ID used to look up the article's original URL.
            sound_redirect_endpoint: Name of function registered in Flask,
                which should be the target of redirects for episode sound files.
                Must accept parameters show, the slug for the show; episode, the
                ID used to look up the episode sound file's original URL;
                title, the original filename for the episode.
            url_for_func: Flask's url_for function.
        """
        self.db_file = db_file
        self.url_service = url_service
        self.article_redirect_endpoint = article_redirect_endpoint
        self.sound_redirect_endpoint = sound_redirect_endpoint
        self.url_for = url_for_func

    def get_original_sound(self, episode):
        """Get the episode sound file's original URL from its intermediate ID.

        Args:
            episode: Intermediate ID for the episode, as passed to the
                sound_redirect_endpoint's episode parameter.

        Returns:
            The URL at which the episode sound file can be found, or None if
            the episode was not recognized.
        """
        with sqlite3.connect(self.db_file) as c:
            r = c.execute("SELECT original FROM sound WHERE proxy=?", (episode,))
            row = r.fetchone()
            if not row:
                return None
            else:
                return row[0]

    def get_original_article(self, article):
        """Get the article's original URL from its intermediate ID.

        Args:
            article: Intermediate ID for the article, as passed to the
                article_redirect_endpoint's article parameter.

        Returns:
            The URL at which the article can be found, or None if the article
            was not recognized.
        """
        with sqlite3.connect(self.db_file) as c:
            r = c.execute("SELECT original FROM article WHERE proxy=?", (article,))
            row = r.fetchone()
            if not row:
                return None
            else:
                return row[0]

    def get_redirect_sound(self, original_url, episode):
        """Obtain the URL listeners should use to access the episode.

        This URL will be handled by this webserver and should just redirect
        the user to the original sound URL. The purpose is to populate the
        access log on this webserver.

        Args:
            original_url: The original URL where the episode sound file resides.
            episode: Instance of Episode to get redirect URL for.

        Returns:
            Intermediate URL listeners should use to access this episode's
            sound file.
        """
        return self._get_redirect_url_for_sound(episode, self._get_url_hash(original_url))
        with sqlite3.connect(self.db_file) as c:
            try:
                r = c.execute("SELECT proxy FROM sound WHERE original=?", (original_url,))
                row = r.fetchone()
                if not row:
                    raise KeyError(episode.media.url)
                return self._get_redirect_url_for_sound(episode, row[0])
            except KeyError:
                new_uri = self._get_url_hash(original_url)
                e = c.execute("INSERT INTO sound (original, proxy) VALUES (?, ?)", (original_url, new_uri))
                return self._get_redirect_url_for_sound(episode, new_uri)

    def _get_redirect_url_for_sound(self, episode, identifier):
        """Utility function for obtaining the intermediate URL for an episode,
        using the intermediate identifier we've found."""
        filename = os.path.basename(
            urllib.parse.unquote(       # Flask quotes for us, don't do it twice
                urllib.parse.urlparse(episode.media.url).path
            )
        )
        return self.url_for(
            self.sound_redirect_endpoint,
            show=self.url_service.sluggify(episode.show.name),
            episode=identifier,
            title=filename,
            _external=True
        )

    def get_redirect_article(self, original_url, episode):
        """Obtain the URL listeners should use to access the article.

        This URL will be handled by this webserver and should just redirect the
        user to the article's actual URL. The purpose is to populate the access
        log on this webserver.

        Args:
            original_url: The original URL where the article resides.
            episode: Instance of Episode to get redirect URL for.

        Returns:
            Intermediate URL listeners should use to acces this episode's
            article.
        """
        show = episode.show
        try:
            with sqlite3.connect(self.db_file) as c:
                try:
                    r = c.execute(
                        "SELECT proxy FROM article WHERE original=?",
                        (original_url,)
                    )
                    row = r.fetchone()
                    if not row:
                        raise KeyError(episode.link)
                    return self._get_redirect_url_for_article(row[0], show)
                except KeyError:
                    new_uri = self._get_url_hash(original_url)
                    e = c.execute(
                        "INSERT INTO article (original, proxy) VALUES (?, ?)",
                        (original_url, new_uri)
                    )
                    return self._get_redirect_url_for_article(new_uri, show)
        except sqlite3.IntegrityError:
            # Either the entry was added by someone else between the SELECT
            # and the INSERT, or the uuid was duplicate.
            # Trying again should resolve both issues.
            return self.get_redirect_article(original_url, episode)

    def _get_redirect_url_for_article(self, identifier, show):
        """Utility function for obtaining the intermediate URL for an episode's
        article, using the intermediate identifier we've found."""
        return self.url_for(
            self.article_redirect_endpoint,
            show=self.url_service.sluggify(show.name),
            article=identifier,
            _external=True
        )

    def _get_url_hash(self, original_url):
        """Generate deterministic intermediate identifier, using the original
        URL."""
        m = hashlib.md5(original_url.encode("UTF-8")).digest()
        return base64.urlsafe_b64encode(m).decode("UTF-8")[:-2]

    def init_db(self):
        """Initialize the database file used by Redirector. Can be called
        independently of whether the database is set up already or not."""
        with sqlite3.connect(self.db_file) as c:
            c.execute("CREATE TABLE IF NOT EXISTS sound "
                      "(original text primary key, proxy text unique)")
            c.execute("CREATE TABLE IF NOT EXISTS article "
                      "(original text primary key, proxy text unique)")

    def get_all_sound(self) -> dict:
        """Get dictionary with intermediate ID as key and original URL as value.
        """
        return self._get_all("sound")

    def get_all_article(self) -> dict:
        """Get dictionary with intermediate ID as key and original URL as value.
        """
        return self._get_all("article")

    def _get_all(self, table):
        result = dict()
        with sqlite3.connect(self.db_file) as c:
            r = c.execute("SELECT proxy, original FROM {}".format(table))

            for row in r:
                result[row[0]] = row[1]

        return result
