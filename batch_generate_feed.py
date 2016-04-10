import argparse
import os.path
from generator.generate_feed import PodcastFeedGenerator
import multiprocessing
from generator import NoEpisodesError, NoSuchShowError
import tempfile
from time import sleep

# Control how many processes can run at any given time
parallels_semaphore = None

def save_feed_to_file(feed, target_file):
    with tempfile.NamedTemporaryFile(delete=False) as fp:
        tempname = fp.name
        fp.write(feed)
    os.replace(tempname, target_file)


def write_feed(show_id, target_file, pretty_xml, durations):
    podcasts = PodcastFeedGenerator(pretty_xml, durations, True)
    try:
        feed = podcasts.generate_feed(show_id, False)
        save_feed_to_file(feed, target_file)
    except (NoSuchShowError, NoEpisodesError):
        # TODO: Log this
        pass
    finally:
        # Make our spot free
        parallels_semaphore.release()


def parse_cli_arguments():
    parser = argparse.ArgumentParser(description="Write feeds for multiple podcasts")

    parser.add_argument("--parallels", type=int, default=1,
                        help="NOT IMPLEMENTED. Number of feeds that can be generated at the same time. Default: 1."
                        "WARNING: Limitations on downloads and memory usage are applied "
                        "PER PARALLEL, so please be conservative or risk running out of memory!")
    parser.add_argument("--create-directory", "-d", action="store_true",
                        help="Create target_dir if it doesn't exist already.")
    parser.add_argument("target_dir", type=os.path.abspath, default=".",
                        help="Directory which the feeds should be saved in.")
    parser.add_argument("naming_scheme", type=str,
                        help="How to name the resulting feeds. The following replacements are made: "
                        "%%T = Title, %%t = title, %%i = DigAS ID")
    parser.add_argument("shows", nargs="*", type=int,
                        help="DigAS IDs for the shows you want to generate feed for. "
                        "Leave it out to generate for all known shows.")
    parser.add_argument("--durations", action="store_true",
                        help="Download episodes and find their durations. "
                        "This could take a ton of time.")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Don't display progress information and other notices.")
    parser.add_argument("--pretty", "-p", action="store_true",
                        help="Write pretty, human-readable XML-files instead of "
                        "machine-generated, minified XML.")

    return parser, parser.parse_args()


def main():
    parser, args = parse_cli_arguments()
    target_dir = args.target_dir
    naming_scheme = args.naming_scheme
    arg_shows = args.shows
    calculate_durations = args.durations
    quiet = args.quiet
    pretty = args.pretty
    create_dir = args.create_directory
    parallels = args.parallels

    all_shows = PodcastFeedGenerator(pretty, calculate_durations, quiet).show_source.shows
    all_shows_set = set(all_shows.keys())
    arg_shows_set = set(arg_shows)
    chosen_shows = all_shows_set.intersection(arg_shows_set)
    if len(arg_shows_set) != len(chosen_shows):
        # Some shows were dropped
        dropped_shows = arg_shows_set - all_shows_set
        parser.error("ERROR: One or more of the given shows were not recognized, namely {shows}."
                     .format(shows=dropped_shows))
    elif not chosen_shows:
        chosen_shows = all_shows_set

    if not os.path.isdir(target_dir):
        if create_dir:
            os.makedirs(target_dir)
        else:
            parser.error("target_dir does not exist and the --create-directory flag is not set.")

    if "%t" not in naming_scheme and "%i" not in naming_scheme and "%T" not in naming_scheme:
        parser.error("naming_scheme must contain %t, %i, %T or a combination in order to generate unique filenames for "
                     "each show.")

    if parallels <= 0:
        parser.error("Argument to --parallels must be positive, not {value}.".format(value=parallels))

    chosen_shows_dict = {show_id: all_shows[show_id].title for show_id in chosen_shows}

    filenames = dict()
    for show_id, show_title in chosen_shows_dict.items():
        # Find the filename
        # Use list of tuples to ensure the last item is actually replaced last
        replacements = [("%T", show_title), ("%t", show_title.lower()), ("%i", str(show_id)), ("%%", "%")]
        filename = naming_scheme
        for search, replace in replacements:
            filename = filename.replace(search, replace)
        if "/" in filename or "\\" in filename:
            filename = filename.replace("/", "_")
            filename = filename.replace("\\", "_")
        filenames[show_id] = os.path.join(target_dir, os.path.normcase(filename))

    if parallels == 1:
        # Run everything in one single process, reusing resources
        g = PodcastFeedGenerator(pretty, calculate_durations, quiet)
        feeds = g.generate_all_feeds_sequence()
        # Save to files
        if not quiet:
            print("Writing feeds to files...")
        for show_id, feed in feeds.items():
            save_feed_to_file(feed, filenames[show_id])
    else:
        # Open one process per feed
        processes = list()
        for show_id, show_title in chosen_shows_dict.items():
            processes.append(multiprocessing.Process(
                target=write_feed,
                args=(show_id, filenames[show_id], pretty, calculate_durations),
                name=show_title
            ))

        global parallels_semaphore
        parallels_semaphore = multiprocessing.BoundedSemaphore(parallels)
        num_feeds = len(processes)
        done_feeds = - parallels

        for i, process in enumerate(processes):
            parallels_semaphore.acquire()
            done_feeds += 1
            print_progress(max(done_feeds, 0), num_feeds, quiet)
            process.start()

        while done_feeds < num_feeds:
            new_done_feeds = num_feeds - len(multiprocessing.active_children())
            if new_done_feeds != done_feeds:
                done_feeds = new_done_feeds
                print_progress(done_feeds, num_feeds, quiet)
            sleep(0.1)


def print_progress(done, all, quiet):
    if not quiet:
        print("({done:03}/{all:03})".format(done=done, all=all), end="\r")


if __name__ == '__main__':
    main()
