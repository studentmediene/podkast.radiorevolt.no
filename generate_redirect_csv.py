import csv

import requests
import sys

from webserver import feed_server, url_service
from generator.episode_source import EpisodeSource
from generate_redirect_rules import get_shows

old = 'http://pappagorg.radiorevolt.no:8080/Podcast/PodcastServlet?rss%s'
new = 'podkast.radiorevolt.no'

def main():
    requests_session = requests.Session()
    requests_session.headers['User-Agent'] = "podcast-feed-gen"
    es = EpisodeSource(requests_session)

    es.populate_all_episodes_list()
    shows = get_shows(False, es)

    rows = []

    feed_server.app.config['SERVER_NAME'] = new
    with feed_server.app.app_context():
        for show in shows:
            new_url = feed_server.url_for_feed(url_service.sluggify(show.name))
            old_url = old % show.id
            rows.append({'source': old_url, 'target': new_url})

        new_url = feed_server.url_for_feed('all')
        old_url = old % ''
        rows.append({'source': old_url, 'target': new_url})

    writer = csv.DictWriter(sys.stdout, fieldnames=['source', 'target'])
    writer.writeheader()
    writer.writerows(rows)

if __name__ == '__main__':
    main()
