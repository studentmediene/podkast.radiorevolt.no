import logging

from flask import request
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


def customize_flask(app, debug=False, update_global_func):
    # Make sure everything works when behind Apache proxy
    app.wsgi_app = ProxyFix(app.wsgi_app)
    # Set debug level to whatever the settings say
    app.debug = debug
    # Make sure we do not use stale data
    app.before_request(update_global_func)
