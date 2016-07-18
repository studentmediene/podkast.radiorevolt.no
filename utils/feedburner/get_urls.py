#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

from sys import stderr
import argparse

from bs4 import BeautifulSoup
import common_feedburner

BASE_URL = "http://feedburner.google.com"
BASE_FEED_URL = "http://feeds.feedburner.com/"


def get_urls(base, debug=False):
    urls = dict()
    b = common_feedburner.get_logged_in_browser(debug=debug)
    shows = common_feedburner.get_feed_pages(b)
    total = len(shows)
    for i, url in enumerate(shows):
        print(
            "Processing show %s out of %s..." % (i + 1, total),
            end="\r",
            file=stderr
        )
        b.load(url, load_timeout=60)

        sh = BeautifulSoup(b.html, "lxml")
        feed_url = sh.select_one('p#thingActions > a')['href'][len(BASE_FEED_URL):]
        try:
            digas_id = int(sh.select_one('input[name="sourceUrl"]')['value'][len(base):])
        except ValueError:
            digas_id = None

        urls[feed_url] = digas_id
    print("", file=stderr)  # Don't mix next output with progress messages
    return urls


def parse_cli_args():
    parser = argparse.ArgumentParser(description="Find which URLs correspond to which show on Feedburner.")
    parser.add_argument("--debug", "-d", action="store_true", help="Watch the browser do its work (yes, this script runs a browser).")
    parser.add_argument("BASE_URL", nargs="?", default="", help="Strip this many characters from the source url (that is, the url  Feedburner "
                        "fetches data from).")
    return parser.parse_args(), parser

def main():
    args, parser = parse_cli_args()
    debug = args.debug
    base = args.BASE_URL
    if not base:
        print("Part of source URLs common for all feeds (will be stripped "
              "away from the source URL to obtain the DigasID): \n> ", end="",
              file=stderr)
        base = raw_input()

    urls = get_urls(
        base,
        debug
    )

    print("ALTERNATE_SHOW_NAMES = {")
    print("\n".join(["    \"%s\": %s," % (url, show_id) for url, show_id in urls.items()]))
    print("}")

if __name__ == '__main__':
    main()
