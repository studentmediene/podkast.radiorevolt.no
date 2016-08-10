import argparse
from generator.generate_feed import PodcastFeedGenerator


def parse_cli_arguments():
    parser = argparse.ArgumentParser(description="Output feed consisting of all episodes from all shows, collected into"
                                                 " a single feed.")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Disable progress messages and notices.")
    parser.add_argument("--pretty", "-p", action="store_true",
                        help="Generate pretty, human-readable XML instead of hard-to-read, minified XML.")
    return parser, parser.parse_args()


def main():
    parser, args = parse_cli_arguments()
    pretty = args.pretty
    quiet = args.quiet

    program = PodcastFeedGenerator(pretty_xml=pretty, quiet=quiet)
    feed = program.generate_feed_with_all_episodes()
    print(feed)

if __name__ == '__main__':
    main()
