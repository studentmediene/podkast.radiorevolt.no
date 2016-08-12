from .manual_changes import ManualChanges
from ...test_utils import *
from pytest import fixture
import os.path as path
import json
from random import random


def write_config(tmpdir, obj):
    # Write configuration file
    filename = path.join(str(tmpdir), "show_manual_changes.json")
    with open(filename, mode="w") as fp:
        json.dump(obj, fp)
    return filename


@fixture()
def config() -> dict:
    return {"0": {"title": "It just works!"}}


@fixture()
def empty_config():
    return dict()


def test_accepts(tmpdir, config, empty_config, requests):
    filename = write_config(tmpdir, config)
    accept_show = show()
    accept_show.show_id = 0
    not_accept_show = show()
    not_accept_show.show_id = 1

    source = ManualChanges({"SHOW_CONFIG": filename}, set(), requests)
    assert source.accepts(accept_show)
    assert not source.accepts(not_accept_show)

    filename2 = write_config(tmpdir, empty_config)
    source_2 = ManualChanges({"SHOW_CONFIG": filename2}, set(), requests)
    assert not source_2.accepts(accept_show)
    assert not source_2.accepts(not_accept_show)


def test_populates(tmpdir, requests):
    show_id = "0"
    cfg = {show_id: {
        "title": "We're no strangers to love",
        "show_url": "http://you.know.the.rules/and/so/do/I",
        "author": "A full commitment's what I'm thinking of",
        "editorial_email": "you.wouldnt.get.this.from.any@other.guy",
        "short_description": "I just wanna tell you how I'm feeling",
        "long_description": "Gotta make you understand",
        "image": "http://nevergonnagive.you/up.png",
        "explicit": True,
        "technical_email": "nevergonnalet@you.down",
        "category": "Never gonna make you cry",
        "sub_category": "Never gonna say good-bye",
        "old": True,
        "language": "en",

    }}
    c = cfg[show_id]
    filename = write_config(tmpdir, cfg)
    sh = show()
    sh.show_id = 0

    source = ManualChanges({"SHOW_CONFIG": filename}, set(), requests)
    source.populate(sh)

    assert sh.title == c['title']
    assert sh.show_url == c['show_url']
    assert sh.author == c['author']
    assert sh.editorial_email == c['editorial_email']
    assert sh.short_description == c['short_description']
    assert sh.long_description == c['long_description']
    assert sh.image == c['image']
    assert sh.explicit == c['explicit']
    assert sh.technical_email == c['technical_email']
    assert sh.category == c['category']
    assert sh.sub_category == c['sub_category']
    assert sh.old == c['old']
    assert sh.language == c['language']


def test_warning_no_config_set(requests):
    source = ManualChanges(dict(), set(), requests)
    with assert_logging(logger):
        assert source.data is None


def test_warning_file_not_exists(requests):
    source = ManualChanges({"SHOW_CONFIG": "thisfiledoesnotexist" + str(random())}, set(), requests)
    with assert_logging(logger):
        assert source.data is None


def test_warning_error_in_file(tmpdir, requests):
    filename = path.join(str(tmpdir), "incorrect.json")
    with open(filename, "w") as fp:
        fp.write("{:}")  # just some incorrect json
    source = ManualChanges({"SHOW_CONFIG": filename}, set(), requests)
    with assert_logging(logger):
        assert source.data is None


def test_warning_unrecognized_option(tmpdir, requests):
    show_id = "0"
    cfg = {show_id: {"show_uri": "http://never.gonna.run/around"}}
    filename = write_config(tmpdir, cfg)

    sh = show()
    sh.show_id = 0

    source = ManualChanges({"SHOW_CONFIG": filename}, set(), requests)
    assert source.data is not None
    with assert_logging(logger):
        source.populate(sh)


def test_bypass(tmpdir, show, config, requests):
    filename = write_config(tmpdir, config)
    show.show_id = 0
    source = ManualChanges({"SHOW_CONFIG": filename}, {show.show_id}, requests)
    assert not source.accepts(show)
    source.bypass.remove(show.show_id)
    assert source.accepts(show)
