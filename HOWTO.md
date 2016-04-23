# How to #

## Adding a new program/show ##

1. Add the new show to DigAS using DigAS Admin.

2. Access `/api/slug/DIGAS PROGRAM NAME HERE` on the podcast website. It will tell you where to find the feed for the program.

3. Activate virtualenv and open up `webserver/test_rr_url.py` and locate the function `rr_urls()`. Add the slug you got from step 2 to the list of urls to test.

4. Run `py.test webserver/`. If there were no errors, you are free to continue. If there was an error, you must fix it before continuing.

5. Reload the changed files by running `touch server.wsgi`.

5. You may now link to the feed on `radiorevolt.no` and afterwards publish it on iTunes. (Note: For Chimera, you will need the DigAS ID. Access the Radio REST API at `/programmer/list/` to find it.)

6. Alter and improve this guide if something was unclear, poorly explained or you encountered a problem which others might want to know the solution for.


## Changing a program's name ##

1. Identify the current URL used to access the show. You may use `/api/slug/DIGAS PROGRAM NAME HERE` on the podcast website to find it.

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



## Upgrading/deploying new version ##

1. Change directory so you're in the folder where podcast-feed-gen is installed.

2. Download the newest changes:

   1. If you want to use newest master:
       ```sh
       git pull
       ```
   2. If you want to use a specific release:
       ```sh
       git fetch --all
       git checkout <release-name>
       ```
3. Go through the changelog and/or release notes, and make the required changes to the configuration files (remember,
   the local non-template files aren't changed).

4. Check that everything works:
   ```sh
   py.test generator webserver
   ```

5. Make the changes live:
   ```sh
   touch server.wsgi
   ```

6. Confirm that it works.

7. …and now that you know that it works on your staging server, it's time to do the same on your production server ;-)

8. Alter and improve this guide if something was poorly explained, you encountered a problem or something similar.