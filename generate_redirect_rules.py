import argparse
import sys
import re
from generator.show_source import ShowSource
from generator.episode_source import EpisodeSource
from generator.no_episodes_error import NoEpisodesError

try:
    from webserver import feed_server
except ImportError:
    print("You must install all the dependencies for the webserver before using this script.", file=sys.stderr)
    sys.exit(1)


def parse_cli_arguments() -> (argparse.ArgumentParser, argparse.Namespace):
    """Parse command line options and return the parser and the parsed Namespace object."""
    parser = argparse.ArgumentParser(description="Generate Apache Redirect rules which can be used to redirect from "
                                     "an old podcast hosting.")
    parser.add_argument("--all", action="store_true",
                        help="Generate rules for all shows. "
                             "Default behaviour is to exclude shows without published episodes.")
    parser.add_argument("--load-module", metavar="PATH_TO_MODULE_DIR", default="",
                        help="Add statements to the beginning that ensures the required mod_rewrite module is loaded.")
    parser.add_argument("--temporary", action="store_true",
                        help="Tell the client that the new location is only temporary. The client should then use the"
                             " old URL the next time as well. Default behaviour is to let the client cache the "
                             "redirect, so the original URL isn't used on subsequent requests.")
    parser.add_argument("old_url", default="OLD ABSOLUTE PATH HERE", nargs="?",
                        help="The old URL scheme, for example \"/Podcast/PodcastServlet?rss%%i\". "
                             "%%i will be replaced by the Digas ID. %%s will be replaced by the new feed slug. "
                             "%%t will be replaced by the show title. Default is just a placeholder.")
    parser.add_argument("new_host",
                        help="Host where podcast-feed-gen will be hosted, for example podcast.example.com.")

    return parser, parser.parse_args()


# We're using mod_rewrite instead of just Rewrite (from mod_alias) because Rewrite cannot operate on query strings.

def get_redirect_rule(show, old_url: str, is_temporary: bool) -> str:
    """
    Get the Rewrite rules needed to perform a redirect from old_url to the show's new url.

    Args:
        show (Show): The Show object which this redirect will target.
        old_url (str): Absolute path which shall be matched, can contain placeholders like %i, %s and %t.
        is_temporary (bool): Set to True to make the temporary temporary (default: permanent)

    Returns:
        str: Rules which makes it so a request to old_url is redirected to the show's new URL.
    """
    rule = ""

    old_url = old_url\
        .replace("%i", str(show.show_id))\
        .replace("%s", feed_server.get_feed_slug(show))\
        .replace("%t", show.title)
    if "?" in old_url:
        # The URL uses a query string, so we must add rules about that
        query_string_start = old_url.find("?")
        query_string = old_url[query_string_start + 1:]
        old_url = old_url[:query_string_start]

        # Include an extra newline to separate different rules from each other
        rule += '\nRewriteCond "%{{QUERY_STRING}}" "^{qs}$"\n'.format(qs=re.escape(query_string))

    new_url = feed_server.url_for_feed(show)

    temporary = "temp" if is_temporary else "permanent"
    rule += 'RewriteRule "^{old}$" "{new}" [R={tmp},L]'.format(old=re.escape(old_url), new=new_url, tmp=temporary)
    return rule


def get_shows(get_all: bool) -> list:
    """
    Get a list of Show objects.

    Args:
        get_all (bool): Set to True to return ALL shows. Defaults to returning shows with published episodes.

    Returns:
        list: List of Show objects.
    """
    show_source = ShowSource()
    all_shows = show_source.shows.values()
    if get_all:
        return all_shows
    else:
        return [show for show in all_shows
                if has_episodes(show)]


def has_episodes(show) -> bool:
    """
    Test if the given Show has any published episodes.

    Args:
        show (Show): Show which shall be tested.

    Returns:
        bool: True if show has episodes, False otherwise.
    """
    try:
        episode_source = EpisodeSource(show)
        episode_source.populate_episodes()
        return True
    except NoEpisodesError:
        return False


def get_load_rules(module_dir: str) -> str:
    """
    Get the rules necessary to use the rewrite module.

    Args:
        module_dir (str): Path to the directory in which the modules are found.

    Returns:
        str: Rules needed to load the mod_rewrite module.
    """
    return "LoadModule rewrite_module {module_dir}/mod_rewrite.so".format(module_dir=module_dir)


def main():
    parser, args = parse_cli_arguments()
    get_all_shows = args.all
    old_url = args.old_url
    new_url = args.new_host
    is_temporary = args.temporary
    include_load_rules = args.load_module

    EpisodeSource.populate_all_episodes_list()

    rules = list()

    if include_load_rules:
        rules.append(get_load_rules(include_load_rules))

    rules.append("RewriteEngine on")

    rules.append("")  # Blank line

    feed_server.app.config['SERVER_NAME'] = new_url
    with feed_server.app.app_context():
        rules.extend([get_redirect_rule(show, old_url, is_temporary)
                      for show in get_shows(get_all_shows)])
    print("\n".join(rules))

if __name__ == '__main__':
    main()
