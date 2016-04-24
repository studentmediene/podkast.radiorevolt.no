import argparse
from generator.generate_feed import PodcastFeedGenerator
from generator.episode_source import EpisodeSource
from generator import settings
from generator.no_episodes_error import NoEpisodesError
from threading import Thread, RLock, active_count, BoundedSemaphore
from sys import stderr
from time import sleep


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
    parser.add_argument("shows", nargs="*", type=int,
                        help="DigAS IDs for the shows you want to calculate durations for. "
                             "Defaults to all shows.")
    return parser, parser.parse_args()


done_episodes = 0


def main():
    parser, args = parse_cli_arguments()
    quiet = args.quiet
    exclude = args.exclude
    args_shows = args.shows
    args_shows_set = set(args_shows)

    generator = PodcastFeedGenerator(quiet=quiet, calculate_durations=False)

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
        parser.error("One or more of the given shows were not recognized, namely {shows}."
                     .format(shows=dropped_shows))

    if not quiet:
        print_err("Collecting episodes...")

    all_episodes = list()
    EpisodeSource.populate_all_episodes_list()
    for show in [all_shows[show_id] for show_id in chosen_shows]:
        try:
            episodes = EpisodeSource(show)
            episodes.populate_episodes()
            all_episodes.extend(episodes.episode_list)
        except NoEpisodesError:
            pass

    episodes_without_duration = [episode for episode in all_episodes if episode.duration is None]

    if not episodes_without_duration:
        parser.exit(message="All episodes have duration information.\n" if not quiet else None)

    settings.FIND_EPISODE_DURATIONS = True
    num_episodes = len(episodes_without_duration)

    if not quiet:
        print_err("{num} episodes need to be fetched. Please be patient.".format(num=num_episodes))

    print_lock = RLock()
    threads = list()
    num_threads = 20
    run_constraint = BoundedSemaphore(num_threads)
    try:
        for episode in episodes_without_duration:
            run_constraint.acquire()
            threads.append(Thread(target=fetch_duration,
                                  kwargs={"episode": episode, "print_lock": print_lock,
                                          "quiet": quiet, "total": num_episodes, "constrain": run_constraint}))
            threads[-1].start()

        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        if not quiet:
            with print_lock:
                print_err("Exiting and cleaning up. Please wait, this could take around one and a half minute...")
        settings.CANCEL.set()
        for thread in threads:
            try:
                thread.join()
            except RuntimeError:
                # The thread may never have been started
                pass


def fetch_duration(episode, print_lock, quiet, total, constrain):
    e = episode.duration
    if not quiet and not settings.CANCEL.is_set():
        print_progress(episode, print_lock, total)
    constrain.release()


def print_progress(episode, print_lock, total):
    with print_lock:
        global done_episodes
        done_episodes += 1
        print_err("{i:04}/{total:04}: {title} done!".format(i=done_episodes, total=total, title=episode.title))


if __name__ == '__main__':
    main()
