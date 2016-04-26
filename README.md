# Podcast feed generator for Radio Revolt #

Generate podcast feeds that can act as drop-in replacement for the existing podcast feeds, and work well with podcast apps.

The main goal is to **eliminate the need for Feedburner**, since Google might shut it down whenever they feel like it.

Below you'll find explainations of how the system works, as well as guides on how to add new programs or change the name of existing ones.

Even though this project is specialized for Radio Revolt, it might be usable for others too – you'd need to create
your own show_source, episode_source and metadata sources though.


## Features ##

* **Use metadata** like episode title, description, image and link from dusken.no/radio and radiorevolt.no (using podcast date to decide which of them to use)
* Use metadata like feed title, description and image from dusken.no/radio or radiorevolt.no (whichever is in use)
* Only publish a podcast episode if its corresponding episode post on dusken.no/radio or radiorevolt.no is published (enabling **preproduction of podcasts**)
* Follow the **guidelines set by iTunes** so that the feed can be used directly by it.
* **Preserve** existing episodes the way they are.


## Technologies ##

This project uses Python v3.4 only, and is written so that the podcast feeds can be updated regularly (by something like
 a cron job) or generated afresh each time a feed is accessed (potentially with a cache).


## Scripts ##

<dl>
    <dt>generate_feed.py</dt>
    <dd>Output RSS feed for a single podcast.</dd>
    <dt>batch_generate_feed.py</dt>
    <dd>Write RSS feeds for all known podcasts.</dd>
    <dt>calculate_durations.py</dt>
    <dd>Write duration information for episodes which don't have it (time consuming!).</dd>
    <dt>server.py</dt>
    <dd>Run web server which generates podcast feeds as they're requested.</dd>
    <dt style="text-decoration: line-through">redirect_server.py</dt>
    <dd>Simple server intended to redirect from our earlier podcast URLs (heavily customized for Radio Revolt)</dd>
    <dt>utils/feedburner_url_fetcher/get_urls.py</dt>
    <dd>Special script for generating <code>SHOW_CUSTOM_URL</code> when Feedburner is in use and the source feed follows a format which ends in the DigAS ID. See <code>README.md</code> in the same directory for installation instructions - its environment differs wildly from the usual one.</dd>

</dl>

Use the `--help` flag to see available options for any script.


## Configuration ##

<dl>
    <dt>generator/settings.py</dt>
    <dd>Settings for feed generation.</dd>
    <dt>webserver/settings.py</dt>
    <dd>Settings for the web server.</dd>
</dl>

## Testing ##

We use `py.test` to run our tests. The test files are located in the same package as the module they test (bad, I know).

### Podcast feed generation ###

While the virtualenv is activated, run
```bash
py.test generator/
```
to run unit tests for the parts of the system that generate podcast feeds. **Code is covered by unit tests only
exceptionally**. We should definitively have many more unit tests!!

The reason you're not advised to run just `py.test` without arguments, is that it would run all the tests found in the
virtualenv folder as well (for example Flask, py.test and so on).

### Podcast feed URLs

Run
```bash
py.test webserver/
```
This will test all the URLs which may be in use by podcatchers around the country, given the long history our podcasts
have. **You MUST run this AT LEAST whenever a program changes its name or a new `ShowMetadataSource` is introduced.**
Ideally, you would set up a script to alert you if any of the tests fail, and run that script daily.

You MUST also maintain `webserver/test_rr_url.py`, by adding a show's new URL when they change name (while keeping the
old URL there, so you can test if the `SHOW_CUSTOM_URL` settings in `webserver/settings.py` and/or
`webserver/settings_template.py` function properly).

## Details: How it works ##

### Generating the feed for a podcast ###

First, the show is matched with one of the shows in `show_source`. It will fetch basic information about the show,
like the show name. In the case of generating the feed for one single podcast, the `show_source` doesn't do much –
its primary purpose is to iterate through all shows.

Next, metadata for the show is fetched by all registered `metadata_sources.show` classes. This is done by querying each
metadata source for whether it has metadata for this show or not. If it has, it is asked to populate the show with new
metadata. The order in which the metadata sources are asked, is defined in `generator/metadata_sources/__init__.py`.
Later sources override information from the earlier ones.

Now, episodes for this podcast are fetched. The `episode_source` is responsible for this.
It also writes basic metadata for all episodes.

Secondly, registered `metadata_sources/episode` classes may act on a subset of the episodes and add or overwrite the existing metadata with
new data, much like the `metadata_sources/show`. Furthermore, each metadata source has a method for figuring out if this
is a relevant episode for this source. If it is, then the metadata source is asked to edit the Episode object.

Both in the case of shows and episodes, multiple metadata sources may act on a single show/episode. This way, one
metadata source may provide only the link to the podcast image, while another source provides the textual description.
Still, if multiple sources provide the same attribute, later metadata sources will override metadata from earlier sources. The order in which the metadata sources appear
in `generator/metadata_sources/__init__.py` is thus of big importance.

Note that it is perfectly acceptable for no metadata source to match an episode or show – in such cases, the default
metadata from the `episode_source` or `show_source` is used, respectively.

### Serving a feed on the web server ###

1. The user requests a feed. This request arrives at the server (assuming the application is deployed). If there is no cache available (or it is stale), the Flask webserver is handed the request.

2. If a query string is used (that is, if podcast.example.org/something?t=15 was accessed), the user is redirected to the same page, but without the query string, going back to step 1. _(This is done to prevent attacks that would fill up the cache)_.

3. The URL is parsed, and a search for the program is made. The search is case-insensitive, and will match the program name, except with no special characters or spaces (only words and numbers are used).

4. If the search is _unsuccessful_, the `ALTERNATE_SHOW_NAMES` dictionary found in `alternate_show_names.py` is searched for a matching key to find either the correct URL slug (which will parsed like in step 3) or the DigAS ID. _(This is done to allow old URLs to continue working)_

5. Now we have a program. If the URL the user used doesn't match the canonical URL (lowercase, no special characters or spaces), then the user is redirected to the canonical URL and the process begins again from step 1.

6. The feed is generated. See the previous section on what happens as a part of that.

7. A processor instruction is injected into the generated XML feed. This instruction tells the browser to use a special stylesheet to give the feed a nice look. That is why the podcast feed doesn't look like an XML feed in for instance Chrome.

8. The appropriate headers are added. They tell the client that this is XML and that this can be cached for up to 1 hour.

9. The response is then handed off to the server. If Apache is running with caching enabled, it will save a copy of the feed and serve that copy the next hour, instead of activating all the machinery above.

