#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

from sys import stderr

import spynner
from bs4 import BeautifulSoup
import getpass

def get_username():
    print("Username for the Google Account: ", end="", file=stderr)
    return raw_input()
def get_password():
    return getpass.getpass(stream=stderr)

def get_login():
    return get_username(), get_password()


def get_logged_in_browser(username=None, password=None, debug=False):
    if not username:
        username = get_username()
    if not password:
        password = get_password()

    print("Logging in...", file=stderr)

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

    return b


def get_feed_pages(browser):
    # Get list of feeds
    browser.load("https://feedburner.google.com/fb/a/myfeeds", load_timeout=60)

    li = BeautifulSoup(browser.html, "lxml")
    return [show.get('href') for show in li.select('td.title > a')]
