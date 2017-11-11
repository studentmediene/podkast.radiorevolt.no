from flask import request, redirect, url_for, abort, make_response, Flask

from .no_episodes_error import NoEpisodesError
from .feed_utils.no_such_show_error import NoSuchShowError
from .feed_utils.show import Show
from .feed_utils.populate import run_episode_pipeline, run_show_pipeline


def xslt_url():
    return url_for('static', filename="style.xsl")


def output_all_feed(all_episodes_settings, all_episodes_ttl, show_source, episode_source, processors):
    show = Show(id=0, **all_episodes_settings)
    show = run_show_pipeline(show, processors['show_all_feed'])
    show = run_show_pipeline(show, processors['show_web'])
    episodes = episode_source.get_all_episodes_list(show_source)
    episodes = run_episode_pipeline(episodes, processors['ep_default'])
    show.episodes = episodes
    return _prepare_feed_response(show, all_episodes_ttl)


def output_feed(show_name, feed_ttl, completed_ttl_factor, alternate_all_episodes_uri, url_service, show_source, episode_source, processors):
    try:
        show, canonical_slug = \
            url_service.get_canonical_slug_for_slug(show_name)
    except NoSuchShowError:
        # Are we perhaps supposed to redirect to /all?
        if show_name.lower() in (name.lower() for name in alternate_all_episodes_uri):
            return redirect(url_for("output_all_feed"))
        else:
            abort(404)
    show_instance = show_source.get_show(show)

    if not show_name == canonical_slug:
        return redirect(url_for_feed(canonical_slug))

    populated_show = run_show_pipeline(
        show_instance, processors['show_default']
    )
    populated_show = run_show_pipeline(
        populated_show, processors['show_web']
    )

    try:
        episodes = episode_source.episode_list(populated_show)
    except NoEpisodesError:
        episodes = []
    populated_episodes = run_episode_pipeline(
        episodes, processors['ep_default']
    )
    populated_show.episodes = populated_episodes

    if populated_show.complete:
        ttl = feed_ttl * completed_ttl_factor
    else:
        ttl = feed_ttl

    return _prepare_feed_response(populated_show, ttl)


def _prepare_feed_response(show, max_age):
    show.xslt = xslt_url()
    feed = show.rss_str()
    resp = make_response(feed)
    resp.headers['Content-Type'] = 'application/xml'
    resp.cache_control.max_age = max_age
    resp.cache_control.public = True
    return resp


def url_for_feed(slug):
    return url_for("output_feed", show_name=slug, _external=True)


def register_feed_routes(app: Flask, settings, get_global):
    def do_output_feed(show_name):
        return output_feed(
            show_name,
            settings['caching']['feed_ttl'],
            settings['caching']['completed_ttl_factor'],
            settings['all_episodes_show_aliases'],
            get_global('url_service'),
            get_global('show_source'),
            get_global('episode_source'),
            get_global('processors'),
        )
    app.add_url_rule("/<show_name>", "output_feed", do_output_feed)

    def do_output_all_feed():
        return output_all_feed(
            settings['feed']['metadata_all_episodes'],
            settings['caching']['all_episodes_ttl'],
            get_global('show_source'),
            get_global('episode_source'),
            get_global('processors'),
        )
    app.add_url_rule("/all", "output_all_feed", do_output_all_feed)
