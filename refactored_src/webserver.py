import threading
import datetime
import logging

from flask import Flask

from .flask_customization import customize_flask, customize_logger
from .web_api import register_api_routes
from .redirects import register_episode_redirect, register_article_redirect
from .web_feed import register_feed_routes
from .settings_loader import load_settings
from .init_globals import init_globals

app = Flask(__name__)

settings = load_settings()

global_values = (None, None)
create_global_lock = threading.RLock()


def get_global_func(*args, **kwargs):
    return global_values[0].get(*args, **kwargs)


def update_global_if_stale():
    global global_values
    with create_global_lock:
        global_dict, expires_at = global_values

        def has_expired():
            return datetime.datetime.now(datetime.timezone.utc) > expires_at

        if global_dict is None or has_expired():
            logging.info("global_values is stale, creating anew…")
            new_global_dict = dict()
            init_globals(new_global_dict, settings, get_global_func)

            now = datetime.datetime.now(datetime.timezone.utc)
            ttl = datetime.timedelta(seconds=settings['caching']['source_data_ttl'])
            new_expire_time = now + ttl

            global_values = (new_global_dict, new_expire_time)


print(repr(settings))
update_global_if_stale()
print(repr(get_global_func()))

customize_logger()
customize_flask(app, update_global_if_stale, debug=settings.get('debug', False))

register_api_routes(app, settings, get_global_func)
register_episode_redirect(app, settings, get_global_func)
register_article_redirect(app, settings, get_global_func)
register_feed_routes(app, settings, get_global_func)
