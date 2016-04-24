#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

from sys import stderr
import argparse

import spynner
from bs4 import BeautifulSoup
import getpass

BASE_URL = "http://feedburner.google.com"
BASE_FEED_URL = "http://feeds.feedburner.com/"


def get_urls(username, password, base, debug=False):
    b = spynner.Browser()
    if debug:
        b.show()
    # Load feedburner
    b.load("http://feedburner.google.com", load_timeout=60)
    # Log in
    b.wk_fill('input[name=Email]', username)
    b.wk_click('#next')
    b.wait_load()
    b.wk_fill('input[name=Passwd]', password)

    b.wk_click('#signIn')

    b.wait_load()

    # Get list of feeds
    b.load("https://feedburner.google.com/fb/a/myfeeds", load_timeout=60)

    urls = dict()

    li = BeautifulSoup(b.html)
    for show in li.select('td.title > a'):
        url = show.get('href')

        b.load(url, load_timeout=60)

        sh = BeautifulSoup(b.html)
        feed_url = sh.select_one('p#thingActions > a')['href'][len(BASE_FEED_URL):]
        try:
            digas_id = int(sh.select_one('input[name="sourceUrl"]')['value'][len(base):])
        except ValueError:
            digas_id = None

        urls[feed_url] = digas_id
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
        print("Part of source URLs common for all feeds: ", end="", file=stderr)
        base = raw_input()

    print("Username for the Google Account: ", end="", file=stderr)
    urls = get_urls(
        raw_input(),
        getpass.getpass(stream=stderr),
        base,
        debug
    )

    print("SHOW_CUSTOM_URL = {")
    print("\n".join(["    \"%s\": %s," % (url, show_id) for url, show_id in urls.items()]))
    print("}")
    print("Done.", file=stderr)

if __name__ == '__main__':
    main()