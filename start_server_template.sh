#!/bin/sh
PODCASTFEEDGEN=<path>
HTTPDPATH=<path>
PORT=<port>

cd $PODCASTFEEDGEN
. venv/bin/activate
mod_wsgi-express start-server server.wsgi --host 127.0.0.1 --port $PORT --httpd-executable=$HTTPDPATH --url-alias /static ./webserver/static
