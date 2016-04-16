from generator.generate_feed import PodcastFeedGenerator
from generator.no_such_show_error import NoSuchShowError
from . import settings
from .redirect import get_original_sound, get_original_article
from flask import Flask, abort, make_response, redirect, url_for

app = Flask(__name__)
app.debug = settings.DEBUG


def find_show(gen: PodcastFeedGenerator, show):
    """Get the Show object for the given show_id or show title."""
    try:
        # Assuming show is show_id
        show_id = int(show)
    except ValueError:
        # Assuming show is show name
        show_id = gen.get_show_id_by_name(show)
    try:
        return gen.show_source.shows[show_id]
    except KeyError as e:
        raise NoSuchShowError from e


def url_for_feed(show):
    return url_for("output_feed", show_name=get_feed_slug(show), _external=True)


def get_feed_slug(show):
    return show.title.lower().replace(" ", "")


@app.route('/<show_name>')
def output_feed(show_name):
    gen = PodcastFeedGenerator(quiet=True)
    try:
        show = find_show(gen, show_name)
    except NoSuchShowError:
        # Perhaps this is an old-style url?
        gen = PodcastFeedGenerator(quiet=True)
        show = show_name.strip().lower()
        for potential_show, show_id in settings.SHOW_CUSTOM_URL.items():
            potential_show = potential_show.lower()
            if potential_show == show:
                return redirect(url_for_feed(gen.show_source.shows[show_id]), 302)
        else:
            abort(404)

    if not show_name == get_feed_slug(show):
        return redirect(url_for_feed(show))

    feed = gen.generate_feed(show.show_id).decode("utf-8")
    # Inject stylesheet processor instruction
    feed = feed.replace("\n",
                        '\n<?xml-stylesheet type="text/xsl" href="' + url_for('static', filename="style.xsl") + '"?>\n',
                        1)
    resp = make_response(feed)
    resp.headers['Content-Type'] = 'application/xml'
    return resp


@app.route('/api/url/<show>')
def api_url_show(show):
    try:
        return url_for_feed(find_show(PodcastFeedGenerator(), show))
    except NoSuchShowError:
        abort(404)


@app.route('/api/url/')
def api_url_help():
    return "<pre>Format:\n/api/url/&lt;show_id&gt;</pre>"


@app.route('/api/')
def api_help():
    alternatives = [
        ("Podkast URLer:", "/api/url/")
    ]
    return "<pre>API for podcast-feed-gen\nFormat:\n" + \
           ("\n".join(["{0:<20}{1}".format(i[0], i[1]) for i in alternatives])) \
           + "</pre>"


@app.route('/episode/<episode>')
def redirect_episode(episode):
    try:
        return redirect(get_original_sound(episode))
    except ValueError:
        abort(404)


@app.route('/artikkel/<article>')
def redirect_article(article):
    try:
        return redirect(get_original_article(article))
    except ValueError:
        abort(404)


@app.route('/')
def redirect_homepage():
    return redirect(settings.OFFICIAL_WEBSITE)
