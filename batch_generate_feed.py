import argparse
import os.path
from generator.generate_feed import PodcastFeedGenerator
import tempfile

def save_feed_to_file(feed, target_file):
    with tempfile.NamedTemporaryFile(delete=False) as fp:
        tempname = fp.name
        fp.write(feed)
    os.replace(tempname, target_file)


def parse_cli_arguments():
    parser = argparse.ArgumentParser(description="Write feeds for multiple podcasts.")
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
                        help="NOT RECOMMENDED: Download episodes and find their durations. "
                        "This takes a TON of time; run calculate_durations.py as a background script instead (so it "
                             "doesn't stop feed generation.")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Disable progress messages and notices.")
    parser.add_argument("--pretty", "-p", action="store_true",
                        help="Write pretty, human-readable XML-files instead of "
                        "hard to read, minified XML.")

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

    generator = PodcastFeedGenerator(pretty, calculate_durations, quiet)
    all_shows = generator.show_source.shows
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

    # Run everything in one single process, reusing resources
    feeds = generator.generate_all_feeds_sequence()
    # Save to files
    if not quiet:
        print("Writing feeds to files...")
    for show_id, feed in feeds.items():
        save_feed_to_file(feed, filenames[show_id])


if __name__ == '__main__':
    main()
