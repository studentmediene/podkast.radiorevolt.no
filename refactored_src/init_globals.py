"""
This module binds the stateful data retrievers to their settings.
"""
import requests
from flask import url_for

from web_utils.url_service import UrlService
from show_source import ShowSource
from episode_source import EpisodeSource
from web_utils.redirector import Redirector
from redirects import SOUND_REDIRECT_ENDPOINT, ARTICLE_REDIRECT_ENDPOINT
from feed_utils.init_pipelines import create_show_pipelines,\
    create_episode_pipelines


def init_globals(new_global_dict: dict, settings: dict, get_global) -> None:
    """
    Create new instances of all data sources, to refresh our data.

    Args:
        new_global_dict: Dictionary to fill with data source instances.
        settings: The settings for the application.
        get_global: Function which takes a parameter and gives the item with
            that key in new_global_dict in return.

    Returns:
        Nothing, new_global_dict is changed in-place.
    """
    requests_session = create_requests()
    show_source = create_show_source(requests_session, settings)
    url_service = create_url_service(settings, show_source)

    new_globals = {
        "requests": requests_session,
        "show_source": show_source,
        "episode_source": create_episode_source(requests_session, settings),
        "processors": {
            "show": create_show_pipelines(
                requests_session, settings, get_global
            ),
            "episode": create_episode_pipelines(
                requests_session, settings, get_global
            ),
        },
        "url_service": url_service,
        "redirector": create_redirector(settings, url_service),
    }

    new_global_dict.update(new_globals)


def create_requests() -> requests.Session:
    """
    Create and configure an instance of requests.Session.
    Returns:
        Instance of requests.Session configured with a user agent string.
    """
    requests_obj = requests.Session()
    requests_obj.headers.update({
        "User-Agent": "podkast.radiorevolt.no",
    })
    return requests_obj


def create_url_service(settings: dict, show_source: ShowSource) -> UrlService:
    """
    Return a configured instance of UrlService, which handles the mapping
    between URIs and the feed to serve.

    Args:
        settings: The application settings, used to find database details.
        show_source: Instance of ShowSource, used to look up existing feeds.

    Returns:
        Configured instance of UrlService.
    """
    return UrlService(settings['db'], show_source)


def create_show_source(
        requests_session: requests.Session,
        settings: dict
) -> ShowSource:
    """
    Return a configured instance of ShowSource, which handles information about
    which shows exist.

    Args:
        requests_session: Object to use when making HTTP requests.
        settings: The application settings, used to configure where to query for
            show information.

    Returns:
        Configured instance of ShowSource.
    """
    api_settings = settings['rest_api']
    return ShowSource(
        requests_session,
        api_settings['url'],
        api_settings['user'],
        api_settings['password']
    )


def create_episode_source(
        requests_session: requests.Session,
        settings: dict
) -> EpisodeSource:
    """
    Return a configured instance of EpisodeSource, which handles information
    about what episode each show has, and the episode's metadata from the
    DigAS database.

    Args:
        requests_session: Object to use when making HTTP requests.
        settings: The application settings, used to configure where to query for
            episode information.

    Returns:
        Configured instance of EpisodeSource.
    """
    return EpisodeSource(
        requests_session,
        settings['rest_api']['url']
    )


def create_redirector(
        settings: dict,
        url_service: UrlService
) -> Redirector:
    """
    Return configured instance of Redirector, used to proxy episode downloads
    through this webserver.

    Args:
        settings: Application settings, used to find path to Redirector's
            database file.
        url_service: Instance of UrlService, used to obtain the canonical slug
            for a given show.

    Returns:
        Configured and initialized instance of Redirector.
    """
    return Redirector(
        settings['redirector']['db_file'],
        url_service,
        ARTICLE_REDIRECT_ENDPOINT,
        SOUND_REDIRECT_ENDPOINT,
        url_for
    )
