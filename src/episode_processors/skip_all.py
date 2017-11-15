from episode_processors import EpisodeProcessor, SkipEpisode


class SkipAll(EpisodeProcessor):
    def accepts(self, episode) -> bool:
        return super().accepts(episode)

    def populate(self, episode) -> None:
        raise SkipEpisode("Skipped because it was accepted by SkipAll")
