# Podcast feed generator for Radio Revolt #

Generate podcast feeds that can act as drop-in replacement for the existing podcast feeds, and work well with podcast apps.

The main goal is to **eliminate the need for Feedburner**, since Google might shut it down whenever they feel like it.

Below you'll find explainations of how the system works, as well as guides on how to add new programs or change the name of existing ones.


## Features ##

* **Use metadata** like episode title, description, image and link from dusken.no/radio and radiorevolt.no (using podcast date to decide which of them to use)
* Use metadata like feed title, description and image from dusken.no/radio or radiorevolt.no (whichever is in use)
* Only publish a podcast episode if its corresponding episode post on dusken.no/radio or radiorevolt.no is published (enabling **preproduction of podcasts**)
* Follow the **guidelines set by iTunes** so that the feed can be used directly by it.
* **Preserve** existing episodes the way they are.


## Technologies ##

This project uses Python v3.4 only, and is written so that the podcast feeds can be updated regularly (by something like
 a cron job) or generated afresh each time a feed is accessed (potentially with a cache).


## How to set up ##

1. Install the following packages (assuming Ubuntu/Debian):

    * libxml2
    * libxml2-dev
    * libxslt1.1
    * libxslt1-dev
    * python3-lxml

    Additionally, install the following packages if you're planning on using the webserver:

    * postgresql
    * python3-dev
    * libpq-dev

    More generally, you need to satisfy the dependencies of the packages listed in the requirement files (see below).

2. Install build dependencies for python and its lxml-bindings by running `sudo apt-get build-dep python3-lxml` (still assuming Ubuntu/Debian)

3. [Use virtualenv!](https://iamzed.com/2009/05/07/a-primer-on-virtualenv/)

   ```bash
   virtualenv -p python3.4 venv
   . venv/bin/activate
   ```

4. Install dependencies by running one of the two commands below. You must decide if you want to run a Python web server for serving freshly generated podcast feeds (recommended), or generate podcast feeds periodically and serve the generated feeds with some other HTTP server.
    <dl>
        <dt>Run web-server and generate feeds on-the-fly</dt>
        <dd><code>pip install -r webserver/requirements.txt</code></dd>
        <dt>Generate feeds periodically</dt>
        <dd><code>pip install -r generator/requirements.txt</code></dd>
    </dl>

5. Copy `generator/settings_template.py` to `generator/settings.py` and fill in settings.
6. Do the same with `webserver/settings_template.py` if you intend to use the provided web server.


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

4. If the search is _unsuccessful_, the `SHOW_CUSTOM_URL` dictionary is searched for a matching key to find either the correct URL slug (which will parsed like in step 3) or the DigAS ID. _(This is done to allow old URLs to continue working)_

5. Now we have a program. If the URL the user used doesn't match the canonical URL (lowercase, no special characters or spaces), then the user is redirected to the canonical URL and the process begins again from step 1.

6. The feed is generated. See the previous section on what happens as a part of that.

7. A processor instruction is injected into the generated XML feed. This instruction tells the browser to use a special stylesheet to give the feed a nice look. That is why the podcast feed doesn't look like an XML feed in for instance Chrome.

8. The appropriate headers are added. They tell the client that this is XML and that this can be cached for up to 1 hour.

9. The response is then handed off to the server. If Apache is running with caching enabled, it will save a copy of the feed and serve that copy the next hour, instead of activating all the machinery above.

## User manual ##

### Adding a new program/show ###

1. Add the new show to DigAS using DigAS Admin.

2. Access `/api/slug/PROGRAM NAME HERE` on the podcast website. It will tell you where to find the feed for the program.

3. Activate virtualenv and open up `webserver/test_rr_url.py` and locate the function `rr_urls()`. Add the slug you got from step 2 to the list of urls to test.

4. Run `py.test webserver/`. If there were no errors, you are free to continue. If there was an error, you must fix it before continuing.

5. You may now link to the feed on `radiorevolt.no` and afterwards publish it on iTunes. (Note: For Chimera, you will need the DigAS ID. Access the Radio REST API at `/programmer/list/` to find it.)

6. Alter and improve this guide if something was unclear, poorly explained or you encountered a problem which others might want to know the solution for.


### Changing a program's name ###

1. Identify the current URL used to access the show. You may use `/api/slug/PROGRAM NAME HERE` on the podcast website to find it.

2. Activate virtualenv and open up `webserver/settings.py`. If there is no variable named `SHOW_CUSTOM_URL` there, then you must open `webserver/settings_template.py` instead.

3. Add a new entry to `SHOW_CUSTOM_URL`.

   1. The key must be the URL slug currently in use. For example, if `podcast.example.org/mylittlepodcast` is the URL currently in use, then you must use `mylittlepodcast` as key.
   2. The value must be the new URL slug. You can find it by accessing `/api/slug/NEW PROGRAM NAME`. Just like the key, you only want to use the slug, not the entire URL.
       * It is possible to use the DigAS ID instead, this is discouraged however since the ID might change if we ever changed system. The name is more logical to use.

4. Open `webserver/test_rr_url.py` and move the current URL slug to the upper part of the list (or add it if it's not there).

5. Run `py.test webserver/` and fix any errors. Note that the new entry in `SHOW_CUSTOM_URL` isn't actually in use right now, but you'll catch any syntax errors this way.

6. Save, upload and deploy the new settings file.

7. Change the show name in DigAS Admin.

8. Add the new URL slug to the bottom half of the list in `webserver/test_rr_url.py`.

9. Run `py.test webserver/` again. The new entry in `SHOW_CUSTOM_URL` should be in use now, so any errors you see will actually affect users. Fix them and deploy and push the changes. It may be the case that the name change hasn't made it to the Radio API yet, so wait a few minutes before testing again if you encounter an error but you're sure you got it right.

10. Add, commit and push the new version of `webserver/test_rr_url.py` (and any other changed files) to GitHub.

11. Alter and improve this guide if something was poorly explained, you encountered a problem or something similar.