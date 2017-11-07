import logging

from flask import request, url_for, redirect, Flask
from werkzeug.contrib.fixers import ProxyFix

from . import set_up_logger


# Set up logging so all log messages include request information
class ContextFilter(logging.Filter):
    # Inject request information into the record
    def filter(self, record):
        if request:
            record.method = request.method
            record.path = request.path
            record.ip = request.remote_addr
            record.agent_platform = request.user_agent.platform
            record.agent_browser = request.user_agent.browser
            record.agent_browser_version = request.user_agent.version
            record.agent = request.user_agent.string
        else:
            record.method = "Outside of request context"
            record.path = ""
            record.ip = ""
            record.agent_platform = ""
            record.agent_browser = ""
            record.agent_browser_version = ""
            record.agent = ""
        return True


def customize_logger():
    # Format the message so that the extra information is outputted
    log_formatter = logging.Formatter(fmt="""\
    ================================================================================
    %(levelname)s while running the web server
        at %(asctime)s
        in %(pathname)s at line %(lineno)s
        PID: %(process)s, thread: %(thread)s, logger: %(name)s

        Request:   %(method)s %(path)s
        IP:        %(ip)s
        Agent:     %(agent_platform)s | %(agent_browser)s %(agent_browser_version)s
        Raw Agent: %(agent)s

    %(message)s
    """
                                      )

    # Put our filter and formatter to use
    set_up_logger.set_up_logger()
    set_up_logger.rotatingHandler.setFormatter(log_formatter)
    set_up_logger.rotatingHandler.addFilter(ContextFilter())


def ignore_get():
    if request.base_url != request.url:
        return redirect(request.base_url, 301)


def redirect_to_favicon():
    return redirect(url_for("static", filename="favicon.ico"))


def redirect_to_website(official_website):
    return redirect(official_website)


def customize_flask(app: Flask, update_global_func, official_website, debug=False):
    # Make sure everything works when behind Apache proxy
    app.wsgi_app = ProxyFix(app.wsgi_app)
    # Set debug level to whatever the settings say
    app.debug = debug
    # Make sure we do not use stale data
    app.before_request(update_global_func)
    # Redirect so we remove query strings (or else, you could circumvent the
    # cache by using arbitrary get parameters)
    app.before_request(ignore_get)
    # Ensure the favicon is available at /favicon.ico (we have no other way of
    # specifying a favicon when serving an XML document)
    app.add_url_rule(
        "/favicon.ico",
        "redirect_to_favicon",
        redirect_to_favicon
    )

    # Ensure / redirects to official website
    def do_redirect_to_website():
        return redirect_to_website(official_website)

    app.add_url_rule(
        "/",
        "redirect_to_website",
        do_redirect_to_website,
    )
