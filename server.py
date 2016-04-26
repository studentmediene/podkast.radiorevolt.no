import webserver.feed_server
import argparse


def parse_cli_arguments():
    parser = argparse.ArgumentParser(description="Run a server suitable for development purposes.")
    parser.add_argument("--debug", "-d", action="store_true",
                        help="Activate debugging, overriding the option in webserver/settings.py "
                             "(you shouldn't use this script in production, but especially not with"
                             " this option!! You might reveal secret information to others.)")
    parser.add_argument("host", nargs="?", default="127.0.0.1", help="Accept connections for this host. "
                        "Set to 0.0.0.0 to enable connections from anywhere (not safe!). "
                        "Defaults to 127.0.0.1, which means only connections from this computer.")
    return parser, parser.parse_args()


if __name__ == '__main__':
    parser, args = parse_cli_arguments()
    host = args.host

    if args.debug:
        webserver.feed_server.app.debug = True
    webserver.feed_server.app.run(host=host)
