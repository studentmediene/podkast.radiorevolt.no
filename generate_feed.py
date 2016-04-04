import argparse
import sys

try:
    from generator import settings
except ImportError:
    sys.exit("ERROR: You have not created generator/settings.py yet.\n"
             "Make a copy of generator/settings_template.py called generator/settings.py and fill in the settings.")

from generator.generate_feed import PodcastFeedGenerator
from generator import NoSuchShowError


def parse_cli_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Output RSS podcast feed for a single podcast.",
                                     epilog="See batch_generate_feed.py if you want to generate feeds for more"
                                            " than one podcast at a time.")
    parser.add_argument("show_id", type=int, help="DigAS ID for the show which shall have its podcast feed generated.")
    durations = parser.add_mutually_exclusive_group()
    durations.add_argument("--durations", action="store_true",
                           help="Include episode durations in the feed. "
                           "This will take a lot of time the first time, because episodes must be downloaded before"
                           " their duration can be calculated.")
    durations.add_argument("--no-durations", action="store_true",
                           help="Do not include episode durations in the feed. Use when time is of essence.")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Disable progress messages.")

    return parser.parse_args()


def main():
    args = parse_cli_arguments()
    show = args.show_id
    durations = args.durations
    no_durations = args.no_durations

    # Check if one of the durations flags are provided.
    if durations or no_durations:
        settings.FIND_EPISODE_DURATIONS = durations

    program = PodcastFeedGenerator()
    try:
        feed = program.generate_feed(show)
        print(feed.decode("utf-8"))
    except NoSuchShowError:
        print("ERROR: No show with ID {0} was found.".format(show), file=sys.stderr)


if __name__ == '__main__':
    main()
