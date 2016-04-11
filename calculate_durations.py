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
                                     "which don't have it yet.")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Disable progress information and notices.")
    return parser, parser.parse_args()


done_episodes = 0


def main():
    parser, args = parse_cli_arguments()
    quiet = args.quiet

    generator = PodcastFeedGenerator(quiet=quiet, calculate_durations=False)
    all_shows = generator.show_source.shows
    all_episodes = list()
    EpisodeSource.populate_all_episodes_list()
    for show in all_shows.values():
        try:
            episodes = EpisodeSource(show)
            episodes.populate_episodes()
            all_episodes.extend(episodes.episode_list)
        except NoEpisodesError:
            pass

    episodes_without_duration = [episode for episode in all_episodes if episode.duration is None]

    if not episodes_without_duration:
        parser.exit(message="All episodes have duration information." if not quiet else None)

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
                print_err("Exiting and cleaning up. Please wait, this could take a minute...")
                # Let the user see the message before we spew out exception traces...
                sleep(2)
        settings.CANCEL.set()
        for thread in threads:
            try:
                thread.join()
            except RuntimeError:
                # The thread may never have been started
                pass


def fetch_duration(episode, print_lock, quiet, total, constrain):
    e = episode.duration
    if not quiet:
        print_progress(episode, print_lock, total)
    constrain.release()


def print_progress(episode, print_lock, total):
    with print_lock:
        global done_episodes
        done_episodes += 1
        print_err("{i:04}/{total:04}: {title} done!".format(i=done_episodes, total=total, title=episode.title))


if __name__ == '__main__':
    main()
