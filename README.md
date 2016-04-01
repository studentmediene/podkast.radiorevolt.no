# Podcast feed generator for Radio Revolt #

Generate podcast feeds that can act as drop-in replacement for the existing podcast feeds, and work well with podcast apps.

The main goal is to **eliminate the need for Feedburner**, since Google might shut it down whenever they feel like it.

## Features ##

* Use metadata like episode title, description, image and link from dusken.no/radio and radiorevolt.no (using podcast date to decide which one to use)
* Use metadate like feed title, description and image from dusken.no/radio or radiorevolt.no (whichever is in use)
* Only publish a podcast episode if its corresponding episode post on dusken.no/radio or radiorevolt.no is published (enabling preproduction of podcasts)
* Follow the guidelines set by iTunes so that the feed can be used directly by it.
* Preserve existing episodes the way they are.

## Technologies ##

This project uses Python v3.4 only, and is written so that the podcast feeds can be updated regularly (by something like a cron job) or generated afresh each time a feed is accessed (potentially with a cache).

## How to set up ##

1. [Use virtualenv!](https://iamzed.com/2009/05/07/a-primer-on-virtualenv/)
2. Run `pip install -r web-server/requirements.txt` if you plan on generating feeds on request, or run `pip install -r generator/requirements.txt` if you plan on just running a cron job.
3. More to come!

