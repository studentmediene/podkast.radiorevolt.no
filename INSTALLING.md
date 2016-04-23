
# How to set up #

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

       [Systemd](http://fedoraproject.org/wiki/Packaging:Systemd):

       1. Copy `systemd/podcast_feed_gen_template.service` and save it as `systemd/podcast_feed_gen.service`.
       2. Fill in the missing username and path.
       3. Run `sudo cp ./podcast_feed_gen.service /etc/systemd/system`
       3. Run `sudo systemctl enable podcast_feed_gen.service`

7. Copy `apache/podcast_feed_gen_template.conf` and save it at `/etc/apache2/sites-available/podcast_feed_gen.conf`
   (or `/etc/httpd/conf.d/podcast_feed_gen.conf`).

8. Edit the file you just created, and fill in the missing information. (Follow the comments in that file.)

8. Run (replace apache or apache2 with httpd if you're using a Redhat distro):

    ```sh
    # Run the following if you have sites-available on your system:
    sudo a2ensite podcast_feed_gen.conf
    # If the following fails, you know you have a configuration error (but the server is still up)
    apachectl configtest
    # Start using the new configuration
    sudo service apache2 restart
    ```

9. Configure DNS so the desired hostname points to your server. Even if `example.com` points to your server, the same
   isn't automatically true for `podcast.example.com`.

   * You can simulate this for testing purposes locally by editing the `/etc/hosts` file
     **on your local computer** and add a line with your server's IP address followed by a tab and `podcast.example.com`.

10. Check if it works. If it doesn't work, you may need to change how SELinux treats the port you're using with
    podcast-feed-gen.
    Check the system logs first, and if that's the problem, run:

    ```sh
    sudo semanage port -a -t http_port_t -p tcp <port>
    ```

10. Run `python calculate_durations.py`. This will actually take several hours (even days!) depending on how many
    episodes there are in the archives. Remember that it is bound to your terminal, so it'll exit if you log out
    of SSH. You should consider running it through `screen` and check in on it the next day.

11. When `calculate_durations.py` is done running the first time, add it to crontab so it runs every hour or every 30 minutes.

    TODO: Be more specific on how to achieve this.

12. There! All happy.