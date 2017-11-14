import argparse
import logging
from collections import namedtuple

from clint.textui import progress

from no_episodes_error import NoEpisodesError
import set_up_logger
from settings_loader import load_settings
from init_globals import init_globals
from web_utils.local_image import LocalImage, ImageIsTooSmall
from feed_utils.populate import prepare_processors_for_batch, run_show_pipeline

logger = logging.getLogger("process_images")


def parse_cli_arguments() -> (argparse.ArgumentParser, argparse.Namespace):
    parser = argparse.ArgumentParser(
        description="Create local copies of all show logos and resize them so they fit iTunes' requirements. "
                    "Note that this script assumes that you're running the webserver on this computer.")
    parser.add_argument("-q", "--quiet", help="Don't generate output.", action="store_true")
    parser.add_argument("-f", "--force", help="Overwrite existing local copies of the logos.", action="store_true")
    parser.add_argument("-e", "--require-episodes", action="store_true",
                        help="Exclude shows which have no associated episodes. "
                             "Note that the episode metadata sources aren't invoked, so a show won't be excluded even if its"
                             " only episode is skipped.")
    return parser, parser.parse_args()


def main():
    parser, args = parse_cli_arguments()
    quiet = args.quiet
    set_up_logger.set_up_logger()
    if quiet:
        set_up_logger.quiet()
    else:
        logging.getLogger("process_images") \
            .addHandler(set_up_logger.mainStreamHandler)
    force = args.force
    require_episodes = args.require_episodes

    settings = load_settings()
    globals = {}
    init_globals(globals, settings, globals.get)

    try:
        prepare_processors_for_batch(
            globals['processors']['show']['image_processing']
        )

        shows = get_shows(require_episodes, force, globals)
        process_images(shows, quiet)
    finally:
        globals['requests'].close()


ShowImagePair = namedtuple("ShowImagePair", ["show", "image"])


def get_shows(require_episodes, force, globals):
    show_source = globals['show_source']
    shows = show_source.get_all_shows()

    populated_shows = []
    for show in shows:
        populated_show = run_show_pipeline(
            show,
            globals['processors']['show']['image_processing']
        )
        populated_shows.append(populated_show)

    shows_w_image = list(filter(lambda s: s.image, populated_shows))

    if require_episodes:
        episode_source = globals['episode_source']

        def has_episode(show):
            try:
                episode_source.episode_list(show)
                return True
            except NoEpisodesError:
                return False

        chosen_shows = list(filter(has_episode, shows_w_image))
    else:
        chosen_shows = shows_w_image

    img_pairs = list(map(lambda s: ShowImagePair(s, LocalImage(s.image)), chosen_shows))

    if force:
        shows_to_process = img_pairs
    else:
        shows_to_process = list(filter(lambda s: not s.image.local_copy_exists(), img_pairs))

    return list(shows_to_process)


def process_images(show_image_pairs, quiet):
    num_images = len(show_image_pairs)

    if not num_images:
        logger.info("There are no images to process.")
        return

    logger.info("Creating local copies of %s images.", num_images)

    for item in progress.bar(show_image_pairs, hide=True if quiet else None):
        show, image = item
        logger.debug("Processing image for %(show)s", {"show": show.name})
        try:
            image.create_local_copy()
        except (IOError, ImageIsTooSmall, RuntimeError):
            logger.exception("An error happened while processing the image "
                             "for %(show)s (image URL: %(url)s).",
                             {"show": show.name, "url": show.image})

if __name__ == '__main__':
    main()
