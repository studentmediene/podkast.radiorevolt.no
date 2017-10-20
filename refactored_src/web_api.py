from flask import abort, url_for, jsonify
import sqlite3

from .feed_utils.no_such_show_error import NoSuchShowError
from .webserver_utils import url_for_feed
from . import url_service


@app.route('/api/url/<show>')
def api_url_show_wrapper(get_global):
    def api_url_show(show):
        try:
            return url_for_feed(url_service.create_slug_for(int(show), get_global['']))
        except (NoSuchShowError, ValueError):
            abort(404)
    return api_url_show


@app.route('/api/url/')
def api_url_help():
    return "<pre>Format:\n/api/url/&lt;DigAS ID&gt;</pre>"


@app.route('/api/slug/')
def api_slug_help():
    return "<pre>Format:\n/api/slug/&lt;show name&gt;</pre>"


@app.route('/api/slug/<show_name>')
def api_slug_name(show_name):
    return url_for('output_feed', show_name=url_service.sluggify(show_name),
                   _external=True)


@app.route('/api/id/')
def api_id():
    json_dict = {"episode": dict(), "article": dict()}
    with sqlite3.connect(settings.REDIRECT_DB_FILE) as c:
        r = c.execute("SELECT proxy, original FROM sound")

        for row in r:
            json_dict['episode'][row[0]] = row[1]

        r = c.execute("SELECT proxy, original FROM article")

        for row in r:
            json_dict['article'][row[0]] = row[1]

    return jsonify(**json_dict)


@app.route('/api/')
def api_help():
    alternatives = [
        ("URL from Digas ID:", "/api/url/"),
        ("Predict URL from show name:", "/api/slug/"),
        ("Get JSON list which maps episode or article identifier to URL:",
         "/api/id/")
    ]
    return "<pre>API for podcast-feed-gen\nFormat:\n" + \
           ("\n".join(["{0:<20}{1}".format(i[0], i[1]) for i in alternatives])) \
           + "</pre>"

def register_api_routes(app, settings):
