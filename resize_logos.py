import argparse
import sys
from generator.generate_feed import PodcastFeedGenerator
import traceback

try:
    from webserver import logo
except ImportError:
    print("You must install all the dependencies for the webserver before using this script. More specifically:",
          file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)


def parse_cli_arguments() -> (argparse.ArgumentParser, argparse.Namespace):
    parser = argparse.ArgumentParser(
        description="Create local copies of all show logos and resize them so they fit iTunes' requirements. "
        "Note that this script assumes that you're running the webserver on this computer.")
    parser.add_argument("-q", "--quiet", help="Don't generate output.", action="store_true")
    parser.add_argument("-f", "--force", help="Overwrite existing local copies of the logos.", action="store_true")
    parser.add_argument("-e", "--require-episodes", action="store_true",
                        help="Exclude shows which have no associated episodes. "
                        "Note that the episode metadata sources aren't invoked, so a show won't be excluded even if its"
                        " only episode is skipped.")
    return parser, parser.parse_args()


def main():
    parser, args = parse_cli_arguments()
    quiet = args.quiet
    force = args.force
    require_episodes = args.require_episodes

    gen = PodcastFeedGenerator(False, quiet)
    if require_episodes:
        logo.LocalImage.create_local_copy_for_all_shows_with_episodes(gen, quiet, force)
    else:
        logo.LocalImage.create_local_copy_for_all_shows(gen, quiet, force)

if __name__ == '__main__':
    main()
