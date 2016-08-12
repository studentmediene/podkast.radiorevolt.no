import argparse
from generator.generate_feed import PodcastFeedGenerator
from generator.episode_source import EpisodeSource
from generator import settings, set_up_logger
from generator.no_episodes_error import NoEpisodesError
from threading import Thread, RLock, BoundedSemaphore
from sys import stderr
import random
from podgen import Media
import logging

logger = logging.getLogger(__name__)


def print_err(*args, **kwargs):
    print(*args, file=stderr, **kwargs)


def parse_cli_arguments():
    parser = argparse.ArgumentParser(description="Write episode durations for episodes "
                                     "which don't have it yet. Those can then be used by generate_feed.py and "
                                     "batch_generate_feed.py so the listeners know how long the episodes are.")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Disable progress information and notices.")
    parser.add_argument("--exclude", "-x", action="store_true",
                        help="Calculate durations for all shows EXCEPT the ones named on the "
                             "command line.")

    def one_or_greater(string):
        value = int(string)
        if value <= 0:
            raise argparse.ArgumentTypeError("%s is not >= 1" % value)
        return value

    parser.add_argument("--parallels", "-p", default=2, type=one_or_greater,
                        help="Number of concurrent downloads. [default: 2]")
    parser.add_argument("shows", nargs="*", type=int,
                        help="DigAS IDs for the shows you want to calculate durations for. "
                             "Defaults to all shows.")
    return parser, parser.parse_args()


done_episodes = 0


def main():
    parser, args = parse_cli_arguments()
    quiet = args.quiet
    exclude = args.exclude
    num_threads = args.parallels
    args_shows = args.shows
    args_shows_set = set(args_shows)

    if quiet:
        set_up_logger.quiet()

    generator = PodcastFeedGenerator(quiet=quiet)

    # Find which shows to use
    all_shows = generator.show_source.shows
    all_shows_set = set(all_shows.keys())
    if exclude:
        chosen_shows = all_shows_set - args_shows_set
    else:
        chosen_shows = args_shows_set
    if not args_shows_set:
        # Default to all shows
        chosen_shows = all_shows_set

    # Were any arguments not recognized?
    dropped_shows = args_shows_set - all_shows_set
    if dropped_shows:
        logger.error("One or more of the given shows were not recognized, namely {shows}."
                     .format(shows=dropped_shows))
        parser.error("Some shows not recognized")

    logger.info("Collecting episodes...")

    all_episodes = list()
    es = EpisodeSource(generator.requests)
    es.populate_all_episodes_list()
    for show in [all_shows[show_id] for show_id in chosen_shows]:
        try:
            all_episodes.extend(es.episode_list(show))
        except NoEpisodesError:
            pass

    episodes_without_duration = [episode for episode in all_episodes if episode.media.duration is None]

    if not episodes_without_duration:
        logger.info("All episodes have duration information")
        parser.exit()

    num_episodes = len(episodes_without_duration)

    logger.info("{num} episodes need to be fetched. Please be patient.".format(num=num_episodes))

    # Shuffle the list of episodes, so that multiple instances at least are
    # unlikely to work on the same episodes
    random.shuffle(episodes_without_duration)

    logger.info("Starting downloads.")

    threads = list()
    run_constraint = BoundedSemaphore(num_threads)
    try:
        for episode in episodes_without_duration:
            run_constraint.acquire()
            threads.append(Thread(target=fetch_duration,
                                  kwargs={"episode": episode, "es": es,
                                          "total": num_episodes, "constrain": run_constraint}))
            threads[-1].start()

        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        logger.warning("Interrupted by user. Exiting and cleaning up. All %s "
                       "downloads that have been started, will be allowed to "
                       "finish. Please wait, this could take several "
                       "minutes...", num_threads)
        settings.CANCEL.set()
        for thread in threads:
            try:
                thread.join()
            except RuntimeError:
                # The thread may never have been started
                pass
    logger.info("Done.")


def fetch_duration(episode, es, total, constrain):
    media = es.media_load(episode.media.url)
    if not media.duration or not media.size:
        episode.media = Media.create_from_server_response(media.url, requests_=es.requests)
        episode.media.fetch_duration()
        es.media_save(episode.media)
    print_progress(episode, total)
    constrain.release()


def print_progress(episode, total):
    global done_episodes
    done_episodes += 1
    logger.debug("{i:04}/{total:04}: {title} done!".format(i=done_episodes, total=total, title=episode.title))


if __name__ == '__main__':
    main()
