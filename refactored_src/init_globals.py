"""
This module binds the stateful data retrievers to their settings.
"""
from itertools import filterfalse

import requests
from flask import url_for

from .web_utils.url_service import UrlService
from .show_source import ShowSource
from .episode_source import EpisodeSource
from . import episode_processors
from . import show_processors
from .web_utils.redirector import Redirector
from .redirects import SOUND_REDIRECT_ENDPOINT, ARTICLE_REDIRECT_ENDPOINT


def init_globals(new_global_dict: dict, settings, get_global):
    requests_session = create_requests()
    show_source = create_show_source(requests_session, settings)
    url_service = create_url_service(settings, show_source)

    new_globals = {
        "requests": requests_session,
        "show_source": show_source,
        "episode_source": create_episode_source(requests_session, settings),
        "processors": {
            "show_default": create_show_processors(
                requests_session, settings, get_global, "default"
            ),
            "ep_default": create_episode_processors(
                requests_session, settings, get_global, "default"
            ),
            "ep_spotify": create_episode_processors(
                requests_session, settings, get_global, "spotify"
            ),
            "show_all_feed": create_show_processors(
                requests_session, settings, get_global, "all_feed"
            ),
        },
        "url_service": url_service,
        "redirector": create_redirector(settings, url_service),
    }

    new_global_dict.update(new_globals)


def create_requests():
    requests_obj = requests.Session()
    requests_obj.headers.update({
        "User-Agent": "podcast-feed-gen",
    })
    return requests_obj


def create_url_service(settings, show_source):
    return UrlService(settings['db'], show_source)


def create_show_source(requests_session, settings):
    api_settings = settings['rest_api']
    return ShowSource(
        requests_session,
        api_settings['url'],
        api_settings['user'],
        api_settings['password']
    )


def create_episode_source(requests_session, settings):
    return EpisodeSource(
        requests_session,
        settings['rest_api']['url']
    )


def create_episode_processors(requests_session, settings, get_global, pipeline):
    return create_processors(requests_session, settings, get_global, "episode", episode_processors, pipeline)


def create_show_processors(requests_session, settings, get_global, pipeline):
    return create_processors(requests_session, settings, get_global, "show", show_processors, pipeline)


def create_processors(requests_session, settings, get_global, pipeline_type, package, pipeline):
    # Each pipeline is a list of dict, iterate over the list
    pipeline_conf = settings['pipelines'][pipeline_type][pipeline]
    initialized_processors = []
    for entry in pipeline_conf:
        # Each entry in a pipeline is a dictionary with a single key: value pair
        # The key is the class to use, the value is the configuration (dict).
        # However, if there is nothing to configure, the entry may be just the
        # class name, which then makes the entry a string.
        if isinstance(entry, dict):
            class_name, local_processor_conf = next(iter(entry.items()))
        elif isinstance(entry, str):
            # Just a string, which means no local configuration
            class_name = entry
            local_processor_conf = {}
        else:
            raise RuntimeError(
                "Did not understand the entry {!r} in pipeline {}.{}. Entry "
                "must be either a dictionary with a single item, or a string."
                .format(entry, pipeline_type, pipeline)
            )

        # Create configuration for this processor, starting with empty dict,
        # overwriting with global processor config and finally config for this
        # appearance in a pipeline specifically
        processor_conf = dict()
        glb_processor_conf = settings['processors'].get(class_name, dict())
        # Ensure we can specify both episodes and shows to bypass for
        # processors which are both show and episode processors
        glb_processor_conf['bypass'] = glb_processor_conf.get(
            'bypass_' + pipeline_type,
            []
        )
        processor_conf.update(glb_processor_conf)
        processor_conf.update(local_processor_conf)

        # Find the constructor
        processor_func = getattr(package, class_name, None)
        if processor_func is None:
            available_classes = get_available_classes(package)
            raise RuntimeError("The class {0} in pipeline {2}.{1} was not found. Available classes: {3}"
                               .format(class_name, pipeline, pipeline_type, available_classes))
        # Use it
        processor = processor_func(processor_conf, processor_conf['bypass'], requests_session, get_global)
        initialized_processors.append(processor)
    return initialized_processors


def get_available_classes(package):
    classes = dir(package)
    classes = filterfalse(lambda c: c.startswith("_"), classes)
    classes = filterfalse(lambda c: c in ('ShowProcessor', 'EpisodeProcessor'),
                          classes)
    classes = filter(lambda c: c[0].isupper(), classes)
    return list(classes)


def create_redirector(settings, url_service):
    return Redirector(
        settings['redirector']['db_file'],
        url_service,
        ARTICLE_REDIRECT_ENDPOINT,
        SOUND_REDIRECT_ENDPOINT,
        url_for
    )
