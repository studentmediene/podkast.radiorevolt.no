import base64

import hashlib

from generator.generate_feed import PodcastFeedGenerator
from generator.no_such_show_error import NoSuchShowError
from generator import metadata_sources
from . import settings, logo
from .alternate_show_names import ALTERNATE_SHOW_NAMES, ALTERNATE_ALL_EPISODES_FEED_NAME
from flask import Flask, abort, make_response, redirect, url_for, request, Response
import re
import shortuuid
import sqlite3
from werkzeug.contrib.fixers import ProxyFix
import urllib.parse
import os.path

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.debug = settings.DEBUG


MAX_RECURSION_DEPTH = 20


def find_show(gen: PodcastFeedGenerator, show, strict=True, recursion_depth=0):
    """Get the Show object for the given show_id or show title."""
    if recursion_depth >= MAX_RECURSION_DEPTH:
        raise RuntimeError("Endless loop encountered in SHOW_CUSTOM_URL when searching for {show}.".format(show=show))
    show_id = None
    if not strict:
        # Assuming show is show_id
        try:
            show_id = int(show)
        except ValueError:
            pass
    if not show_id:
        # Assuming show is show name
        try:
            show_id = gen.get_show_id_by_name(show)
        except (KeyError, NoSuchShowError) as e:
            # Perhaps this is an old-style url?
            gen = PodcastFeedGenerator(quiet=True)
            show = show.strip().lower()
            for potential_show, show_id in ALTERNATE_SHOW_NAMES.items():
                potential_show = potential_show.lower()
                if potential_show == show:
                    return find_show(gen, show_id, False, recursion_depth + 1)
            else:
                raise NoSuchShowError from e
    try:
        return gen.show_source.shows[show_id]
    except KeyError as e:
        raise NoSuchShowError from e


def url_for_feed(show):
    return url_for("output_feed", show_name=get_feed_slug(show), _external=True)


def xslt_url():
    return url_for('static', filename="style.xsl")

remove_non_word = re.compile(r"[^\w\d]|_")


def get_feed_slug(show):
    return get_readable_slug_from(show.name)


def get_readable_slug_from(show_name):
    return remove_non_word.sub("", show_name.lower())


@app.before_request
def ignore_get():
    if request.base_url != request.url:
        return redirect(request.base_url, 301)


@app.route('/all')
def output_all_feed():
    gen = PodcastFeedGenerator(quiet=True, xslt=xslt_url(), pretty_xml=True)
    gen.register_redirect_services(get_redirect_sound, get_redirect_article)

    feed = gen.generate_feed_with_all_episodes()
    return _prepare_feed_response(feed, 10 * 60)


@app.route('/<show_name>')
def output_feed(show_name):
    # Replace image so it fits iTunes' specifications
    metadata_sources.SHOW_METADATA_SOURCES.append(logo.ReplaceImageURL)
    # Make it pretty, so curious people can learn from it
    gen = PodcastFeedGenerator(quiet=True, xslt=xslt_url(), pretty_xml=True)
    try:
        show = find_show(gen, show_name)
    except NoSuchShowError:
        # Are we perhaps supposed to redirect to /all?
        if show_name.lower() in (name.lower() for name in ALTERNATE_ALL_EPISODES_FEED_NAME):
            return redirect(url_for("output_all_feed"))
        else:
            abort(404)

    if not show_name == get_feed_slug(show):
        return redirect(url_for_feed(show))

    PodcastFeedGenerator.register_redirect_services(get_redirect_sound, get_redirect_article)

    feed = gen.generate_feed(show.id)
    return _prepare_feed_response(feed, 60 * 60)


def _prepare_feed_response(feed, max_age) -> Response:
    resp = make_response(feed)
    resp.headers['Content-Type'] = 'application/xml'
    resp.cache_control.max_age = max_age
    resp.cache_control.public = True
    return resp


@app.route('/api/url/<show>')
def api_url_show(show):
    try:
        return url_for_feed(find_show(PodcastFeedGenerator(quiet=True), show, False))
    except NoSuchShowError:
        if show.lower() in (name.lower() for name in ALTERNATE_ALL_EPISODES_FEED_NAME):
            return url_for("output_all_feed", _external=True)
        else:
            abort(404)


@app.route('/api/url/')
def api_url_help():
    return "<pre>Format:\n/api/url/&lt;DigAS ID or show name&gt;</pre>"


@app.route('/api/slug/')
def api_slug_help():
    return "<pre>Format:\n/api/slug/&lt;show name&gt;</pre>"


@app.route('/api/slug/<show_name>')
def api_slug_name(show_name):
    return url_for('output_feed', show_name=get_readable_slug_from(show_name), _external=True)


@app.route('/api/')
def api_help():
    alternatives = [
        ("Podkast URLs:", "/api/url/"),
        ("Predict URL from show name:", "/api/slug/"),
    ]
    return "<pre>API for podcast-feed-gen\nFormat:\n" + \
           ("\n".join(["{0:<20}{1}".format(i[0], i[1]) for i in alternatives])) \
           + "</pre>"


@app.route('/episode/<show>/<episode>/<title>')
def redirect_episode(show, episode, title):
    try:
        return redirect(get_original_sound(find_show(PodcastFeedGenerator(quiet=True), show), episode))
    except ValueError:
        abort(404)


@app.route('/artikkel/<show>/<article>')
def redirect_article(show, article):
    try:
        return redirect(get_original_article(find_show(PodcastFeedGenerator(quiet=True), show), article))
    except ValueError:
        abort(404)

@app.route('/')
def redirect_homepage():
    return redirect(settings.OFFICIAL_WEBSITE)


def get_redirect_db_connection():
    return


def get_original_sound(show, episode):
    with sqlite3.connect(settings.REDIRECT_DB_FILE) as c:
        r = c.execute("SELECT original FROM sound WHERE proxy=?", (episode,))
        row = r.fetchone()
        if not row:
            abort(404)
        else:
            return row[0]

def get_original_article(show, article):
    with sqlite3.connect(settings.REDIRECT_DB_FILE) as c:
        r = c.execute("SELECT original FROM article WHERE proxy=?", (article,))
        row = r.fetchone()
        if not row:
            abort(404)
        else:
            return row[0]


def get_redirect_sound(original_url, episode):
    show = episode.show
    with sqlite3.connect(settings.REDIRECT_DB_FILE) as c:
        try:
            r = c.execute("SELECT proxy FROM sound WHERE original=?", (original_url,))
            row = r.fetchone()
            if not row:
                raise KeyError(episode.media.url)
            return redirect_url_for(episode, row[0])
        except KeyError:
            new_uri = get_url_hash(original_url)
            e = c.execute("INSERT INTO sound (original, proxy) VALUES (?, ?)", (original_url, new_uri))
            return redirect_url_for(episode, new_uri)


def redirect_url_for(episode, identifier):
    filename = os.path.basename(urllib.parse.urlparse(episode.media.url).path)
    return url_for("redirect_episode", show=get_feed_slug(episode.show), episode=identifier,
                   title=filename, _external=True)


def get_redirect_article(original_url, episode):
    show = episode.show
    try:
        with sqlite3.connect(settings.REDIRECT_DB_FILE) as c:
            try:
                r = c.execute("SELECT proxy FROM article WHERE original=?", (original_url,))
                row = r.fetchone()
                if not row:
                    raise KeyError(episode.link)
                return url_for("redirect_article", show=get_feed_slug(show), article=row[0], _external=True)
            except KeyError:
                new_uri = get_url_hash(original_url)
                e = c.execute("INSERT INTO article (original, proxy) VALUES (?, ?)", (original_url, new_uri))
                return url_for("redirect_article", show=get_feed_slug(show), article=new_uri, _external=True)
    except sqlite3.IntegrityError:
        # Either the entry was added by someone else between the SELECT and the INSERT, or the uuid was duplicate.
        # Trying again should resolve both issues.
        return get_redirect_article(original_url, episode)


def get_url_hash(original_url):
    m = hashlib.md5(original_url.encode("UTF-8")).digest()
    return base64.urlsafe_b64encode(m).decode("UTF-8")[:-2]


@app.before_first_request
def init_db():
    with sqlite3.connect(settings.REDIRECT_DB_FILE) as c:
        c.execute("CREATE TABLE IF NOT EXISTS sound (original text primary key, proxy text unique)")
        c.execute("CREATE TABLE IF NOT EXISTS article (original text primary key, proxy text unique)")
