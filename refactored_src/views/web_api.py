from flask import abort, jsonify, Flask

from feed_utils.no_such_show_error import NoSuchShowError
from views.web_feed import url_for_feed


def api_url_show(show, url_service):
    try:
        return url_for_feed(url_service.create_slug_for(int(show)))
    except (NoSuchShowError, ValueError):
        abort(404)

def api_url_help():
    return "<pre>Format:\n/api/url/&lt;DigAS ID&gt;</pre>"


def api_slug_help():
    return "<pre>Format:\n/api/slug/&lt;show name&gt;</pre>"


def api_slug_name(show_name, url_service):
    return url_for_feed(url_service.sluggify(show_name))


def api_id(redirector):
    json_dict = {"episode": redirector.get_all_sound(), "article": redirector.get_all_article()}

    return jsonify(**json_dict)


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


def register_api_routes(app: Flask, settings, get_global):
    # Functions for giving functions access to some globals, letting them
    # access globals through the get_global in this context, creating closures
    def inject_url_service(func):
        def func_with_url_service(*args, **kwargs):
            kwargs['url_service'] = get_global('url_service')
            return func(*args, **kwargs)
        return func_with_url_service

    def inject_redirector(func):
        def func_with_redirector(*args, **kwargs):
            kwargs['redirector'] = get_global('redirector')
            return func(*args, **kwargs)
        return func_with_redirector

    # Define which URLs maps to what functions
    app.add_url_rule(
        "/api/url/<show>",
        "api_url_show",
        inject_url_service(api_url_show)
    )

    app.add_url_rule(
        "/api/url/",
        "api_url_help",
        api_url_help
    )

    app.add_url_rule(
        "/api/slug/",
        "api_slug_help",
        api_slug_help
    )

    app.add_url_rule(
        "/api/slug/<show_name>",
        "api_slug_name",
        inject_url_service(api_slug_name)
    )

    app.add_url_rule(
        "/api/id/",
        "api_id",
        inject_redirector(api_id)
    )

    app.add_url_rule(
        "/api/",
        "api_help",
        api_help
    )
