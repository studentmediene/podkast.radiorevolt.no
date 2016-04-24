import argparse
import sys

# Give helpful message if settings isn't available
try:
    from generator import settings
except ImportError:
    sys.exit("ERROR: You have not created generator/settings.py yet.\n"
             "Make a copy of generator/settings_template.py called generator/settings.py and fill in the settings.")

from generator.generate_feed import PodcastFeedGenerator
from generator import NoSuchShowError


def parse_cli_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Output RSS podcast feed for a single podcast. It is printed to "
                                                 "standard output.",
                                     epilog="See batch_generate_feed.py if you want to generate feeds for more"
                                            " than one podcast at a time. See calculate_durations.py if you want to "
                                            "find podcast durations for all episodes.")
    parser.add_argument("show_id", type=int, help="DigAS ID for the show which shall have its podcast feed generated.")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Disable progress messages and notices.")
    parser.add_argument("--pretty", "-p", action="store_true",
                        help="Generate pretty, human-readable XML instead of hard-to-read, minified XML.")

    return parser.parse_args()


def main():
    args = parse_cli_arguments()
    show = args.show_id
    pretty_xml = args.pretty
    quiet = args.quiet

    program = PodcastFeedGenerator(pretty_xml=pretty_xml, quiet=quiet)
    try:
        feed = program.generate_feed(show)
        print(feed.decode("utf-8"))
    except NoSuchShowError:
        print("ERROR: No show with ID {0} was found.".format(show), file=sys.stderr)


if __name__ == '__main__':
    main()
