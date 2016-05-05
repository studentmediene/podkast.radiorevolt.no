# How to #

## Add a new program/show ##

1. Add the new show to DigAS using DigAS Admin.

2. Access `/api/slug/DIGAS PROGRAM NAME HERE` on the podcast website. It will tell you where to find the feed for the program.

3. Activate virtualenv and open up `webserver/test_rr_url.py` and locate the function `rr_urls()`. Add the slug you got from step 2 to the list of urls to test.

4. Run `py.test webserver/`. If there were no errors, you are free to continue. If there was an error, you must fix it before continuing.

5. Reload the changed files by running `touch server.wsgi`.

6. You may now link to the feed on `radiorevolt.no` and afterwards publish it on iTunes. (Note: For Chimera, you will need the DigAS ID. Access the Radio REST API at `/programmer/list/` to find it.)

7. Alter and improve this guide if something was unclear, poorly explained or you encountered a problem which others might want to know the solution for.


## Change a program's name ##

1. Identify the current URL used to access the show. You may use `/api/slug/DIGAS PROGRAM NAME HERE` on the podcast website to find it.

2. Activate virtualenv and open up `webserver/alternate_show_names.py`.

3. Add a new entry to `ALTERNATE_SHOW_NAMES`.

   1. The key must be the URL slug currently in use. For example, if `podcast.example.org/mylittlepodcast` is the URL currently in use, then you must use `mylittlepodcast` as key.
   2. The value must be the new URL slug. You can find it by accessing `/api/slug/NEW PROGRAM NAME`. Just like the key, you only want to use the slug, not the entire URL.
       * It is possible to use the DigAS ID instead, this is discouraged however since the ID might change if we ever changed system. The name is more logical to use.

4. Open `webserver/test_rr_url.py` and move the current URL slug to the upper part of the list (or add it if it's not there).

5. Run `py.test webserver/` and fix any errors. Note that the new entry in `ALTERNATE_SHOW_NAMES` isn't actually in use right now, but you'll catch any syntax errors this way.

6. Save, upload and deploy the new settings file.

7. Change the show name in DigAS Admin.

8. Add the new URL slug to the bottom half of the list in `webserver/test_rr_url.py`.

9. Run `py.test webserver/` again. The new entry in `ALTERNATE_SHOW_NAMES` should be in use now, so any errors you see will actually affect users. Fix them and deploy and push the changes. It may be the case that the name change hasn't made it to the Radio API yet, so wait a few minutes before testing again if you encounter an error but you're sure you got it right.

10. Add, commit and push the new version of `webserver/test_rr_url.py` (and any other changed files) to GitHub.

11. Alter and improve this guide if something was poorly explained, you encountered a problem or something similar.



## Upgrade/deploy a new version ##

You might want to have a staging server which is identical to the production server, and first try to upgrade the
staging server before upgrading the production server.

1. Change directory so you're in the folder which contains the folder where podcast-feed-gen is installed.

2. Make a copy of the podcast-feed-gen folder:

    ```sh
    cp -p -R podcast-feed-gen upgrade-podcast-feed-gen
    ```

    You might have to run this with sudo.

3. Change into the new directory:

    ```sh
    cd upgrade-podcast-feed-gen
    ```

4. Remove the virtualenv.

    ```sh
    rm -R venv
    ```

5. Set up the `virtualenv` and install the required packages, following the instructions in `INSTALLING.md`.

6. Download the newest changes:

   1. If you want to use newest master:

       ```sh
       git pull
       ```
   2. If you want to use a specific release:

       ```sh
       git fetch --all
       git checkout <release-name>
       ```
7. Go through the changelog and/or release notes, and make the required changes to the configuration files (remember,
   the local non-template files aren't changed). You may also need to install or upgrade existing dependencies.

8. Make yourself the owner of the data directory, so you can run the tests:

    ```sh
    sudo chown -R YOUR_USERNAME:YOUR_USERNAME data
    ```

8. Check that everything works:

   ```sh
   . venv/bin/activate
   py.test generator webserver
   ```

9. Change back so the podcastfeedgen user you created during installation owns the data directory:

    ```sh
    sudo chown -R SERVER_USER:SERVER_USER data
    ```

9. Now, we're ready to make our changes live. First, deactivate the virtualenv before removing it:

    ```sh
    deactivate
    rm -R venv
    ```

10. Step out of the temporary directory.

    ```sh
    cd ..
    ```

11. **While performing the following steps, the website may become unavailable and produce errors!**

    First, check if there are any specific instructions about this upgrade, like installing a new dependency or upgrading
    one of the existing dependencies. Follow those instructions.

12. Copy the new files:

    ```sh
    cp -p -u -R upgrade-podcast-feed-gen/. podcast-feed-gen
    ```

    You might need to run this with sudo.

13. Make the server reload, so the changes are applied:

    ```sh
    touch podcast-feed-gen/server.wsgi
    ```

13. Access the website and confirm that nothing is broken.

14. **Now, the website should be back to normal.**

15. Remove the copy we created.

    ```sh
    rm -R upgrade-podcast-feed-gen
    ```

    You might need to run this with sudo.

16. Alter and improve this guide if something was poorly explained, you encountered a problem or something similar.
