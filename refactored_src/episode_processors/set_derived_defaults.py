from . import EpisodeProcessor


class SetDerivedDefaults(EpisodeProcessor):
    """
    Set fields in the episode that can be derived from other existing fields.

    Specifically, this creates a short summary out of the long summary if the
    latter exists and not the first. Secondly, the episode's ID is set to the
    media URL if it's not set already.
    """
    def accepts(self, episode) -> bool:
        return super().accepts(episode)

    def populate(self, episode) -> None:
        has_summary = episode.summary is not None
        has_long_summary = episode.long_summary is not None
        if not has_summary and has_long_summary:
            # Use the first line in long description (or everything if there's no newline)
            first_newline = episode.long_summary.find("\n")
            episode.summary = episode.long_summary[:first_newline] if first_newline != -1 else episode.long_summary
        if episode.id is None:
            episode.id = episode.media.url
