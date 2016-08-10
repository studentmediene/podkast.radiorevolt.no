import requests
from .settings import EPISODE_SOURCE as SETTINGS
from .no_episodes_error import NoEpisodesError
from .episode import Episode
import threading
import datetime
import time
import sqlite3
from podgen import Media, Person, htmlencode
import pickle
import re


_urlfinderregex = re.compile(r'http([^\.\s]+\.[^\.\s<>]*)+[^\.\s<>]{2,}')


def linkify(text: str, maxlinklength: int=50):
    def replacewithlink(matchobj):
        url = matchobj.group(0)
        text = str(url)
        if text.startswith('http://'):
            text = text.replace('http://', '', 1)
        elif text.startswith('https://'):
            text = text.replace('https://', '', 1)

        if text.startswith('www.'):
            text = text.replace('www.', '', 1)

        if len(text) > maxlinklength:
            halflength = maxlinklength // 2
            text = text[0:halflength] + '...' + text[len(text) - halflength:]

        return '<a href="' + url + '">' + text + '</a>'

    if text is not None and text != '':
        return _urlfinderregex.sub(replacewithlink, text)
    else:
        return ''

class EpisodeSource:
    """Class for fetching episodes for podcasts.
    """

    def __init__(self, request_session: requests.Session):
        """
        Initialize an episode source.

        Args:
            request_session (requests.Session): The Requests session which will be used when fetching data.
        """

        self.all_episodes = None
        """List of all episodes, regardless of show, sorted with the most recent first."""

        self.fetch_episode_lock = threading.RLock()
        """Lock ensuring only one thread fetches and parses list of all episodes."""

        self.episodes_by_show = dict()
        """Dictionary with Show ID as key, and a list of episodes as value."""

        self.requests = request_session
        """Requests session to be used when performing requests."""

    def _fetch_all_episodes(self) -> list:
        """Fetches a list with all the episodes in the database, regardless of show."""
        episode_list = self.requests.get(
            url=SETTINGS['RADIO_REST_API_URL'] + "/lyd/podcast/"
        ).json()
        return episode_list

    def populate_all_episodes_list(self):
        """Fetch all podcast episodes. Saves time when processing multiple shows."""
        with self.fetch_episode_lock:
            if self.all_episodes is None:
                self.all_episodes = self._fetch_all_episodes()

    def _fetch_episodes_for(self, show_id: int) -> list:
        """Returns a list with all the episodes in the database for the given show ID."""
        episode_list = self.requests.get(
            url=SETTINGS['RADIO_REST_API_URL'] + "/lyd/podcast/" + str(show_id)
        ).json()
        return episode_list

    def _get_episode_data(self, show):
        """Return list of all episodes for this show, using the all_episodes list if appropriate."""

        # Determine whether all episodes are downloaded in batch or not
        with self.fetch_episode_lock:
            use_all_episodes = self.all_episodes is not None

        if not use_all_episodes:
            # Fetch episodes for this show only
            episodes = self._fetch_episodes_for(show.id)
        else:
            # Use the existing list of episodes and find the relevant ones
            episodes = [episode for episode in self.all_episodes if episode['program_defnr'] == show.id]

        if not episodes:
            raise NoEpisodesError(show.id)
        else:
            return episodes

    def episode_list(self, show):
        """List of Episode objects for the given show."""
        if show.id not in self.episodes_by_show:
            try:
                self.episodes_by_show[show.id] = [self.episode(show, episode_dict)
                                                       for episode_dict in self._get_episode_data(show)]
            except NoEpisodesError as e:
                # TODO: Check if any code depend on an empty list being returned the second time this method is called, refactor and remove the following line.
                self.episodes_by_show[show.id] = []
                raise e
        return self.episodes_by_show[show.id]

    def media_load(self, sound_url):
        """Return a Media object for a given sound url."""
        db = None
        try:
            # Create a new database connection (a new one each time, because
            # of threading)
            db = sqlite3.connect(SETTINGS['MEDIA_OBJECTS_DB'])
            db.execute("PRAGMA busy_timeout = 30000")
            # Try to fetch the media object
            c = db.execute("SELECT obj FROM media WHERE id=?", (sound_url,))
            value = c.fetchone()
            c.close()
            # Did we get it?
            if value:
                return pickle.loads(value[0])
            else:
                # Nope, we have to live without size and duration
                return Media(sound_url)
        finally:
            if db:
                db.close()

    def media_save(self, media_obj):
        db = sqlite3.connect(SETTINGS['MEDIA_OBJECTS_DB'])
        db.execute("PRAGMA busy_timeout = 30000")
        try:
            update = self.media_load(media_obj.url).duration

            if not update:
                try:
                    db.execute("INSERT INTO media (id, obj) VALUES (:id, :obj)",
                               {"id": media_obj.url, "obj": pickle.dumps(media_obj)})
                except sqlite3.IntegrityError:
                    # There is already an entry for this episode – someone else
                    # has saved while we were busy, so just update it
                    update = True
            if update:
                db.execute("UPDATE media SET obj=:obj WHERE id=:id",
                           {"id": media_obj.url, "obj": pickle.dumps(media_obj)})
            db.commit()
        finally:
            if db:
                db.close()


    def episode(self, show, episode_dict):
        return Episode(
            show=show,
            media=self.media_load(episode_dict['url']),
            title=episode_dict['title'],
            summary=linkify(htmlencode(episode_dict['comment']))
                .replace("\n", "<br/>\n"),
            publication_date=datetime.datetime.strptime(str(episode_dict['dato']) + " 12:00:00 " + time.strftime("%z"),
                                            "%Y%m%d %H:%M:%S %z"),
            authors=[Person(name=episode_dict['author'])] if episode_dict['author'] else [],
        )


def create_media_table():
    _create_table = sqlite3.connect(SETTINGS['MEDIA_OBJECTS_DB'])
    _create_table.execute(
        "create table if not exists media (id text primary key, obj blob)")

    _create_table.close()

create_media_table()
