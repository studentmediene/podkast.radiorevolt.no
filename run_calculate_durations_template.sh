#!/bin/sh
PODCASTFEEDGEN=<path>
VIRTUALENV=$PODCASTFEEDGEN/venv

cd PODCASTFEEDGEN
. VIRTUALENV/bin/activate
python calculate_durations.py
