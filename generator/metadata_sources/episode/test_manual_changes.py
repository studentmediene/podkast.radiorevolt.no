from .manual_changes import ManualChanges
from ...test_utils import *
from pytest import fixture, raises
import os.path as path
import json
from random import random
import pytz
import datetime


def write_config(tmpdir, obj):
    # Write configuration file
    filename = path.join(str(tmpdir), "episode_manual_changes.json")
    with open(filename, mode="w") as fp:
        json.dump(obj, fp)
    return filename


@fixture()
def config() -> dict:
    return {"example_url": {"title": "It just works!"}}


@fixture()
def empty_config():
    return dict()


def test_accepts(tmpdir, config, empty_config):
    filename = write_config(tmpdir, config)
    accept_episode = episode()
    accept_episode.sound_url = iter(config.keys()).__next__()
    not_accept_episode = episode()

    source = ManualChanges({"EPISODE_CONFIG": filename}, set())
    assert source.accepts(accept_episode)
    assert not source.accepts(not_accept_episode)

    filename2 = write_config(tmpdir, empty_config)
    source_2 = ManualChanges({"EPISODE_CONFIG": filename2}, set())
    assert not source_2.accepts(accept_episode)
    assert not source_2.accepts(not_accept_episode)


def test_populates(tmpdir):
    sound_url = "Oooh"
    cfg = {sound_url: {
        "title": "We're no strangers to love",
        "article_url": "http://you.know.the.rules/and/so/do/I",
        "date": "2016-04-04 16:00:00 +0200",
        "author": "A full commitment's what I'm thinking of",
        "author_email": "you.wouldnt.get.this.from.any@other.guy",
        "short_description": "I just wanna tell you how I'm feeling",
        "long_description": "Gotta make you understand",
        "image": "http://nevergonnagive.you/up.png",
        "explicit": True  # sorry not sorry
    }}
    c = cfg[sound_url]
    filename = write_config(tmpdir, cfg)
    ep = episode()
    ep.sound_url = iter(cfg.keys()).__next__()

    source = ManualChanges({"EPISODE_CONFIG": filename}, set())
    source.populate(ep)

    assert ep.title == c['title']
    assert ep.article_url == c['article_url']
    assert ep.date == datetime.datetime(2016, 4, 4, 16, 0, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=2)))
    assert ep.author == c['author']
    assert ep.author_email == c['author_email']
    assert ep.short_description == c['short_description']
    assert ep.long_description == c['long_description']
    assert ep.image == c['image']
    assert ep.explicit == c['explicit']


def test_warning_no_config_set(capsys):
    source = ManualChanges(dict(), set())
    assert source.data is None
    assert len(capsys.readouterr()[1])


def test_warning_file_not_exists(capsys):
    source = ManualChanges({"EPISODE_CONFIG": "thisfiledoesnotexist" + str(random())}, set())
    assert source.data is None
    assert len(capsys.readouterr()[1])


def test_warning_error_in_file(capsys, tmpdir):
    filename = path.join(str(tmpdir), "incorrect.json")
    with open(filename, "w") as fp:
        fp.write("{:}")  # just some incorrect json
    source = ManualChanges({"EPISODE_CONFIG": filename}, set())
    assert source.data is None
    assert len(capsys.readouterr()[1])


def test_warning_unrecognized_option(capsys, tmpdir):
    sound_url = "http://never.gonna.let/you/down.mp3"
    cfg = {sound_url: {"article_uri": "http://never.gonna.run/around"}}
    filename = write_config(tmpdir, cfg)

    ep = episode()
    ep.sound_url = sound_url

    source = ManualChanges({"EPISODE_CONFIG": filename}, set())
    assert source.data is not None
    source.populate(ep)
    assert len(capsys.readouterr()[1])


def test_bypass(tmpdir, episode, config):
    filename = write_config(tmpdir, config)
    episode.sound_url = iter(config.keys()).__next__()
    source = ManualChanges({"EPISODE_CONFIG": filename}, {episode.sound_url})
    assert not source.accepts(episode)
    source.bypass.remove(episode.sound_url)
    assert source.accepts(episode)




