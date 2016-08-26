#!/bin/sh
# Fill in the missing values below
PODCASTFEEDGEN=<path>
PORT=<port>
WORKERS=<workers>

cd $PODCASTFEEDGEN
. venv/bin/activate
gunicorn -b 127.0.0.1:$PORT -w $WORKERS --max-requests 500 --max-requests-jitter 50 webserver.feed_server:app
