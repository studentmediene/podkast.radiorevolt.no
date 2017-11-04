"""
This module binds the stateful data retrievers to their settings.
"""
from itertools import filterfalse

import requests

from .show_source import ShowSource
from .episode_source import EpisodeSource
from . import episode_processors
from . import show_processors


def init_globals(new_global_dict: dict, settings):
    requests_session = create_requests()

    new_globals = {
        "requests": requests_session,
        "show_source": create_show_source(requests_session, settings),
        "episode_source": create_episode_source(requests_session, settings),
        "processors": {
            "show_default": create_show_processors(
                requests_session, settings, "default"
            ),
            "ep_default": create_episode_processors(
                requests_session, settings, "default"
            ),
            "ep_spotify": create_episode_processors(
                requests_session, settings, "spotify"
            ),
        },
        "url_service": create_url_service(settings),
        "redirector": create_redirector(settings),
    }

    new_global_dict.update(new_globals)


def create_requests():
    requests_obj = requests.Session()
    requests_obj.headers.update({
        "User-Agent": "podcast-feed-gen",
    })
    return requests_obj


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


def create_episode_processors(requests_session, settings, pipeline):
    return create_processors(requests_session, settings, "episode", episode_processors, pipeline)


def create_show_processors(requests_session, settings, pipeline):
    return create_processors(requests_session, settings, "show", show_processors, pipeline)


def create_processors(requests_session, settings, pipeline_type, package, pipeline):
    # Each pipeline is a list of dict, iterate over the list
    pipeline_conf = settings['pipelines'][pipeline_type][pipeline]
    initialized_processors = []
    for entry in pipeline_conf:
        # Each entry in a pipeline is a dictionary with a single key: value pair
        # The key is the class to use, the value is the configuration (dict)
        class_name, local_processor_conf = next(iter(entry.items()))

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
        processor = processor_func(processor_conf, processor_conf['bypass'], requests_session)
        initialized_processors.append(processor)


def get_available_classes(package):
    classes = dir(package)
    classes = filterfalse(lambda c: c.startswith("_"), classes)
    classes = filterfalse(lambda c: c in ('ShowProcessor', 'EpisodeProcessor'),
                          classes)
    classes = filter(lambda c: c[0].isupper(), classes)
    return list(classes)
