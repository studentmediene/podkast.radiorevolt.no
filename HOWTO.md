# How to #

## Monitor logs ##

Run `tail -F data/application.log` in a terminal window (when in the application
directory). Replace `application.log` with `application.warnings.log` to see
only warnings and errors.

## Application complains about Permission denied ##

Try running the following:

`sudo chown -R podprod data src/static/images`

Replace `podprod` with whatever user is used to run the application.

Please note that the application should not be the owner of any other directory
or file than those mentioned above, in order to minimize consequences of a
security breach.

## Change name of show

Simply change the name in DigAS. You should monitor the logs for warnings and
errors.

## Add support for an alternate version of feeds

This is how the Spotify feed is set up.

1. Add pipeline name to `ALLOWED_PIPELINES` in `src/views/web_feed.py`.
2. Add pipeline to the set given to `validate_pipelines` in the functions
   `create_show_pipelines` and `create_episode_pipelines` found in
   `src/feed_utils/init_pipelines.py`.
3. Add configuration for this pipeline in `settings.default.yaml`, with an
   explanatory comment.
4. Test out the application. You should be able to access this pipeline through
   `/<pipeline-name>/<show-name>`.

## Upgrade/deploy a new version ##

You might want to have a staging server which is identical to the production server, and first try to upgrade the
staging server before upgrading the production server.

1. Change directory so you're in the folder which contains the folder where this application is installed.

2. Make a copy of the podkast.radiorevolt.no folder:

    ```sh
    cp -p -R podkast.radiorevolt.no upgrade-podkast.radiorevolt.no
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

5. Set up the `virtualenv` and install the required packages, following the instructions in `README.md`.

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

8. Make yourself the owner of the data directory, so you can run the tests (note: no tests exist, this is outdated. Instead, run python src/app.py --bind 0.0.0.0:9000 or something to test out the application.):

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
    
   (There's a chance you may have to restart the podcast-feed-gen service/upstart thing instead, 
   I don't know for sure. In that case: `sudo service podcast_feed_gen restart` or 
   `sudo systemctl podcast_feed_gen restart`.)

13. Access the website and confirm that nothing is broken.

14. **Now, the website should be back to normal.**

15. Remove the copy we created.

    ```sh
    rm -R upgrade-podcast-feed-gen
    ```

    You might need to run this with sudo.

16. Alter and improve this guide if something was poorly explained, you encountered a problem or something similar.
