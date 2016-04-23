import argparse
import sys
from generator.show_source import ShowSource
from generator.episode_source import EpisodeSource
from generator.no_episodes_error import NoEpisodesError

try:
    from webserver import feed_server
except ImportError:
    print("You must install all the dependencies for the webserver before using this script.", file=sys.stderr)
    sys.exit(1)


def parse_cli_arguments():
    parser = argparse.ArgumentParser(description="Generate Apache Redirect rules which can be used to redirect from "
                                     "an old podcast hosting.")
    parser.add_argument("--all", action="store_true",
                        help="Generate rules for all shows. "
                             "Default behaviour is to exclude shows without published episodes.")
    parser.add_argument("--temporary", action="store_true",
                        help="Tell the browser that the new location is only temporary. The browser should then use the"
                             " old URL the next time as well.")
    parser.add_argument("old_url", default="OLD ABSOLUTE PATH HERE", nargs="?",
                        help="The old URL scheme, for example \"/Podcast/PodcastServlet?rss%%i\". "
                             "%%i will be replaced by the Digas ID. %%s will be replaced by the new feed slug. "
                             "%%t will be replaced by the show title.")
    parser.add_argument("new_host",
                        help="Host where podcast-feed-gen will be hosted, for example podcast.example.com.")

    return parser, parser.parse_args()


def get_redirect_rule(show, old_url: str, is_temporary):
    old_url = old_url\
        .replace("%i", str(show.show_id))\
        .replace("%s", feed_server.get_feed_slug(show))\
        .replace("%t", show.title)
    new_url = feed_server.url_for_feed(show)
    temporary = "temp" if is_temporary else "permanent"
    return """Redirect {tmp} "{old}" "{new}\"""".format(old=old_url, new=new_url, tmp=temporary)


def get_shows(get_all: bool):
    show_source = ShowSource()
    all_shows = show_source.shows.values()
    if get_all:
        return all_shows
    else:
        return [show for show in all_shows
                if has_episodes(show)]


def has_episodes(show):
    try:
        episode_source = EpisodeSource(show)
        episode_source.populate_episodes()
        return True
    except NoEpisodesError:
        return False


def main():
    parser, args = parse_cli_arguments()
    get_all_shows = args.all
    old_url = args.old_url
    new_url = args.new_host
    is_temporary = args.temporary

    EpisodeSource.populate_all_episodes_list()

    feed_server.app.config['SERVER_NAME'] = new_url
    with feed_server.app.app_context():
        rules = [get_redirect_rule(show, old_url, is_temporary) for show in get_shows(get_all_shows)]
    print("\n".join(rules))

if __name__ == '__main__':
    main()
