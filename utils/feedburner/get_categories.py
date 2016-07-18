#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

from sys import stderr
import argparse

from bs4 import BeautifulSoup
import common_feedburner
import json
import re


def get_categories(base, debug=False):
    categories = dict()
    b = common_feedburner.get_logged_in_browser(debug=debug)
    shows = common_feedburner.get_feed_pages(b)
    print("Found %s shows." % len(shows), file=stderr)
    total = len(shows)
    for i, url in enumerate(shows):
        print("Collecting category for show %s out of %s..." % (i + 1, total),
              end="\r", file=stderr)
        # Manipulate url so it loads the page with podcast options
        url = url.replace("dashboard", "smartcast", 1)

        b.load(url, load_timeout=60)

        sh = BeautifulSoup(b.html, "lxml")
        digas_id = sh.select_one('input[name="sourceUrl"]')['value'][len(base):]

        category = unicode(sh.select_one('div#iTunesOptions > ul > li > select > option[selected]').string)
        js = unicode(sh.select_one('div#smartCast > form > script:nth-of-type(2)').string)
        sub_category =  re.search(r"\n\n\n\nsubtopicValue = \"(.*)\";\n\n//this decodes any &amp;s it finds"+\
                         r" so that these literal subtopic values match when the dropdowns are built\nsubtopicValue = "
                         r"subtopicValue\.unescapeHTML\(\);\n\n        //if not blank, set subtopic select with matching "
                         r"value to 'selected'\nif \(subtopicValue\.length > 0\) \{\n        "
                         r"itunesSubtopics\.forField\(\"services\(enclosure\)\.subtopic1\"\)\.setValues\(subtopicValue\);\n\}",
                                  js)\
        .group(1).replace("&amp;", "&")

        if category == u"(None)":
            category = None
        if sub_category == u"No subcategory" or not sub_category:
            sub_category = None

        if category is None:
            continue
        elif sub_category is None:
            category_tuple = (category,)
        else:
            category_tuple = (category, sub_category)

        categories[digas_id] = category_tuple

    print("", file=stderr)  # Don't blend next output with progress messages
    return categories


def parse_cli_args():
    parser = argparse.ArgumentParser(description="Find what category is used for each Feedburner feed.")
    parser.add_argument("--debug", "-d", action="store_true", help="Watch the browser do its work (yes, this script runs a browser).")
    parser.add_argument("BASE_URL", nargs="?", default="", help="Strip this many characters from the source url to "
                                                                "obtain the DigasID.")
    return parser.parse_args(), parser


def main():
    args, parser = parse_cli_args()
    debug = args.debug
    base = args.BASE_URL
    if not base:
        print("Part of source URLs common for all feeds (will be stripped "
              "away from the source URL to obtain the DigasID):\n> ", end="",
              file=stderr)
        base = raw_input()

    categories = get_categories(
        base,
        debug
    )

    # Convert to format expected by ManualChanges
    category_data = {digas_id: {"category": category}
                     for digas_id, category in categories.items()}

    print(json.dumps(category_data, indent=4))

if __name__ == '__main__':
    main()
