import requests
import feedgen
import argparse

from . import settings
from . import metadata_sources
from . import episode_source


def parse_cli_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Output RSS podcast feed for a single podcast.",
                                     epilog="See batch_generate_feed.py if you want to generate feeds for more"
                                            " than one podcast at a time.")
    parser.add_argument("show", type=int, help="DigAS ID for the show which shall have its podcast feed generated.")

    return parser.parse_args()


def main():
    args = parse_cli_arguments()



if __name__ == '__main__':
    main()
