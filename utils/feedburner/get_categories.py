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
    for url in shows:
        # Manipulate url so it loads the page with podcast options
        url = url.replace("dashboard", "smartcast", 1)

        b.load(url, load_timeout=60)

        sh = BeautifulSoup(b.html)
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

        categories[digas_id] = (category, sub_category)

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
        print("Part of source URLs common for all feeds: ", end="", file=stderr)
        base = raw_input()

    categories = get_categories(
        base,
        debug
    )

    # Convert to format compatible with manual_changes
    categories_data = dict()
    for digas_id, category in categories.items():
        entry = dict()
        if category[0]:
            entry["category"] = category[0]
            if category[1]:
                entry["sub_category"] = category[1]
        categories_data[digas_id] = entry

    print(json.dumps(categories_data, indent=4))

if __name__ == '__main__':
    main()
