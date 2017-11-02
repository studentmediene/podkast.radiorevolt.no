import requests

from show_source import ShowSource


def init_globals(new_global_dict: dict, settings):
    requests_session = create_requests()

    new_globals = {
        "requests": requests_session,
        "show_source": create_show_source(requests_session, settings),
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
        api_settings['username'],
        api_settings['password']
    )


