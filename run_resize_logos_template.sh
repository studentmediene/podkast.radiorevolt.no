#!/bin/sh
PODCASTFEEDGEN=<path>
VIRTUALENV=$PODCASTFEEDGEN/venv

cd $PODCASTFEEDGEN
. $VIRTUALENV/bin/activate
python resize_logos.py -e
