
# Installing podcast-feed-gen #

## Getting it up and running ##

1. Install the following packages (assuming Ubuntu/Debian):

    * libxml2
    * libxml2-dev
    * libxslt1.1
    * libxslt1-dev
    * python3-lxml

    Additionally, install the following packages if you're planning on using the webserver:

    * apache2-bin
    * apache2-dev

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


### Deploying to Apache ###

1. Create a new user. In this guide it is called `podcastfeedgen`, but you may pick whatever name you prefer.

    ```
    sudo useradd podcastfeedgen
    ```

2. Follow the above instructions, installing it into `/srv/podcast-feed-gen` (or another location outside of `/home`)
   and with a different owner than `podcastfeedgen`. That way, the script is unable to modify itself. You can change
   the owner after setting it up by running:

   ```sh
   sudo chown -R <user>:<user> .
   ```

3. Give the new user access to the data folder.

    ```
    sudo chown podcastfeedgen:podcastfeedgen data
    ```

4. Make sure debugging is turned off in the configuration files.

5. Make sure the Apache webserver for podcast-feed-gen is started on startup.

   1. Copy `start_server_template.sh` to `start_server.sh` and fill in the variables at the top of the script.

   2. [Upstart](http://upstart.ubuntu.com/cookbook/):

       1. Copy `upstart/podcast_feed_gen_template.conf` and save it as `upstart/podcast_feed_gen.conf`.
       2. Fill in the missing username and path.
       3. Run `sudo cp upstart/podcast_feed_gen.conf /etc/init/podcast-feed-gen.conf`

       [Systemd](https://wiki.archlinux.org/index.php/systemd):

       1. Copy `systemd/podcast_feed_gen_template.service` and save it as `systemd/podcast_feed_gen.service`.
       2. Fill in the missing username and path.
       3. Run `sudo cp ./podcast_feed_gen.service /etc/systemd/system`
       3. Run `sudo systemctl enable podcast_feed_gen.service`

7. Copy `apache/podcast_feed_gen_template.conf` and save it at `/etc/apache2/sites-available/podcast_feed_gen.conf`
   (or `/etc/httpd/conf.d/podcast_feed_gen.conf` if Red Hat).

8. Edit the file you just created, and fill in the missing information. (Follow the comments in that file.)

8. Run (replace apache2 with httpd if you're using a Red Hat distro):

    ```sh
    # Run the following if you have sites-available on your system:
    sudo a2ensite podcast_feed_gen.conf
    # If the following fails, you know you have a configuration error (but the server is still up)
    apachectl configtest
    # Start actually using the new configuration
    sudo service apache2 restart
    ```

9. Configure DNS so the desired hostname points to your server. Even if `example.com` points to your server, the same
   isn't automatically true for `podcast.example.com`.

   * You can simulate this for testing purposes locally by editing the `/etc/hosts` file
     **on your local computer** and add a line with your server's IP address followed by a tab and `podcast.example.com`.

10. Check if it works. If it doesn't work, you may need to change how SELinux treats the port you're using with
    podcast-feed-gen. Apache isn't allowed to send and listen to every port on the system by default.
    Check the system logs first, and if this is the problem, grant Apache access to the port podcast-feed-gen runs on:

    ```sh
    sudo semanage port -a -t http_port_t -p tcp <port>
    ```

10. Run `python calculate_durations.py` while the virtualenv is activated.
    This will actually take several hours (even days!) depending on how many
    episodes there are in the archives. Remember that it is bound to your terminal, so it'll exit if you log out
    of SSH. You should consider [running it through `screen`](https://www.rackaid.com/blog/linux-screen-tutorial-and-how-to/) and check in on it the next day.

    To start it: run `screen`, then navigate to the directory, activate the virtualenv and run the script. Hit
    `Ctrl+A` followed by `d` to detach yourself while it's running. You may then log off SSH.

    To check it: run `screen -r` to reattach yourself. You may then detach again if it's not done, or exit if it's done.


11. When `calculate_durations.py` is done running the first time, add it to crontab so it runs every 30 minutes.

    1. Copy `run_calculate_durations_template.sh` and save it as `run_calculate_durations.sh`.
    2. Edit it and fill in the path to podcast-feed-gen.
    3. Run:

       ```sh
       sudo crontab -e
       ```
    4. Append the following line, filling in the user (`podcastfeedgen`) and the path to the script.
       ```
       2,32 * * * * /usr/bin/sudo -u <user> <path>/run_calculate_durations.sh 2>&1 >/dev/null
       ```
       It will run HH:02 and HH:32. The offset 2 was chosen with random.org, to avoid having many tasks run at HH:00.

12. There! All happy.

## Deploying redirection from old podcast server ##

This guide applies to you if you have a server which you used to generate podcast feeds with, but which you want to
replace with podcast-feed-gen, yet it doesn't occupy the same address. For example, say you have a server which serves
feeds like `internal.example.com:8080/Podcast/PodcastServlet?rss451` where `451` is the DigAS ID. You have already
deployed podcast-feed-gen on `podcast.example.com`, but you want to make sure existing subscribers get to enjoy the new
feeds as well. That problem is a perfect fit for the `generate_redirect_rules.py` script.

It is assumed you are somewhat comfortable editing Apache configuration files, as well as using the Linux command line.

1. You must use a computer on which webserver/requirements.txt is fulfilled. This is because the
    `generate_redirect_rules.py` script depends on some scripts inside webserver.

2. Activate the virtualenv.

3. Find the old path scheme. In the above example, it would be `/Podcast/PodcastServlet?rss%i`. Run
    `python generate_redirect_rules.py --help` for the full list of substitutions that are made.

4. Find the new host on which podcast-feed-gen is hosted. In the above example, this would be `podcast.example.com`

5. Now, run the following command (install `xclip` if it's not installed already):
    ```sh
    python generate_redirect_rules.py "OLD PATH SCHEME HERE" "NEW HOST HERE" | xclip -selection clipboard
    ```
    This will copy the generated rules to the clipboard.

6. Log onto the old host (or preferably its staging cousin).

7. Add a new file in `/etc/apache2/conf-available` or `/etc/apache2/sites-available` (Debian/Ubuntu) or `/etc/httpd/conf.d` (Red Hat/Fedora) and call it
    something like `redirect_podcasts.conf`. Or, you can use the existing file where the old implementation is hosted.

8. Open it and paste the generated rules.

9. Make adjustments to the rules as needed. For example, you might want to limit the redirects to certain virtual hosts
    and/or ports.

10. Save the file and exit.

11. On Debian/Ubuntu: run the correct `a2enSOMETHING` command (`a2enconf` if you used conf-available, `a2ensite` if you
    used sites-available).

12. Check if the configuration is alright by running `apachectl configtest`.

13. Reload the changes by running `sudo service apache2 restart` (Debian/Ubuntu) or
    `sudo systemctl restart httpd` (Red Hat/Fedora).

14. Confirm that it works, then eat cake.
