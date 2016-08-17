import os.path
import logging
from urllib.parse import urlparse, unquote
from flask import url_for
from PIL import Image
import requests
import io
import tempfile
from warnings import warn
import warnings
from generator.metadata_sources.show_metadata_source import ShowMetadataSource
from generator.episode_source import EpisodeSource
from generator.no_episodes_error import NoEpisodesError
import sys
import traceback
from cached_property import threaded_cached_property as cached_property
from clint.textui import progress


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ImageIsTooSmall(UserWarning):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

warnings.simplefilter('error', Image.DecompressionBombWarning)


class LocalImage:
    image_directory = os.path.join(os.path.dirname(__file__), "static", "images")
    """Directory in which images are to be saved. Changes must be made before creating any instance of this class."""
    # Assuming square image sizes
    min_image_size = 1400
    """Minimum width and height in pixels for images."""
    max_image_size = 3000
    """Maximum width and height in pixels for images."""

    def __init__(self, original_url: str):
        self.original_url = original_url

    @cached_property
    def filename(self) -> str:
        """The filename of this image; or the filename it should have had if it existed locally."""
        return os.path.splitext(
            os.path.basename(
                unquote(
                    urlparse(
                        self.original_url
                    ).path
                )
            )
        )[0] + ".png"

    @cached_property
    def path(self) -> str:
        """The absolute path to a local copy of this image; or the path it should have had if it existed locally."""
        return os.path.join(self.image_directory, self.filename)

    def get_image_url(self) -> str:
        """Get the absolute URL which is to be used for the given original image URL.

            If a local copy exists for this image, the url for that is returned. If it does not, the original url is
            returned untouched.
            """
        if self.local_copy_exists():
            return self.url_to_local_image
        else:
            return self.original_url

    @cached_property
    def url_to_local_image(self) -> str:
        """Get the absolute URL for a local image with the given filename."""
        # Assuming the image directory is directly beneath the static folder
        return url_for("static", filename=os.path.join(os.path.basename(self.image_directory), self.filename),
                       _external=True)

    def local_copy_exists(self) -> bool:
        """Returns true if a local image with the given filename exists."""
        return os.path.exists(self.path)

    @classmethod
    def _resize(cls, original_image, new_image, url: str=""):
        """Create a properly resized image.

        Args:
              original_image: File object with the original image.
              new_image: File object in which the new, resized image is to be written.
        """
        img = Image.open(original_image)

        new_width, new_height = cls._calculate_new_image_size(img, cls.min_image_size, cls.max_image_size, url)
        # Skip resizing if there's no change in size
        new_img = cls._create_resized_image(img, new_width, new_height) if (new_width, new_height) != img.size else img
        new_img.save(new_image, "png", optimize=True)

    @staticmethod
    def _create_resized_image(image: Image.Image, width: int, height: int) -> Image.Image:
        """Return a new copy of image, except it has the given width and height."""
        # While it might look like we could have used Image.thumbnail, it is not appropriate since the image
        # might need to be upscaled
        return image.resize((width, height), Image.LANCZOS)

    @staticmethod
    def _calculate_new_image_size(img: Image.Image, min_size: int, max_size: int,
                                  url: str="") -> (int, int):
        """Figure out the new dimensions for the provided image.

        It will preserve aspect ratio and will be between min_size and max_size.

        Args:
            img: Image which will be inspected (to get the current dimensions).
            min_size: Minimum size for both width and height (in pixels).
            max_size: Maximum size for both width and height (in pixels).
        Raises:
            RuntimeError: When the image cannot possibly fit the requirements without altering the aspect ratio or crop.

        Warnings:
            ImageIsTooSmall: When the image must be increased in size in order to fit the requirements. You really should
                replace the image with a larger one.
        """
        delta = 10.0   # be 10 pixels too small or too big when resizing, just to be on the safe side
        too_large = max(img.size) > max_size
        too_small = min(img.size) < min_size
        width, height = img.size

        if too_large and too_small:
            # This image exceeds the limit in one direction, but is too short along the other.
            raise RuntimeError("The image cannot possibly be resized while maintaining its aspect ratio, "
                               "since it is both too small and too big. Try to make it into a square.")

        # Find the factor (since we're keeping the aspect ratio)

        #   new_width   new_height
        #   --------- = ----------
        #     width       height
        if too_large:
            width_is_biggest = max(img.size) == width
            if width_is_biggest:
                factor = (max_size - delta) / width
            else:
                factor = (max_size - delta) / height
        elif too_small:
            warn("{url} is {width}x{height}. Will be upscaled to {min}x{min}."
                 .format(width=width, height=height, min=min_size, url=url),
                 ImageIsTooSmall)
            width_is_smallest = min(img.size) == width
            if width_is_smallest:
                factor = (min_size + delta) / width
            else:
                factor = (min_size + delta) / height
        else:
            # No resize needed, so keep it as it is
            factor = 1.0

        new_width = round(width * factor)
        new_height = round(height * factor)

        # Check the new width and height
        if max(new_width, new_height) > max_size or min(new_width, new_height) < min_size:
            raise RuntimeError("The image cannot possibly be resized while maintaining its aspect ratio, "
                               "since its form is too different from a square. Try to make the logo closer to a square.")

        return new_width, new_height

    def create_local_copy(self):
        """Create a local, properly resized copy of this image."""
        r = requests.get(self.original_url)
        r.raise_for_status()
        original_image = io.BytesIO(r.content)

        # Write resized image to temporary file, before moving it to its intended location
        new_image = None
        try:
            new_image = tempfile.NamedTemporaryFile("w+b", delete=False)
            # Write to the temporary file
            self._resize(original_image, new_image, self.original_url)
            new_image.close()
            original_image.close()
            # Overwrite the possibly existing image, as an atomic action
            os.replace(new_image.name, self.path)
        except Exception:
            if new_image:
                os.remove(new_image.name)
            raise

    def create_local_copy_if_not_exists(self):
        """Create a local, properly resized copy of this image, if it doesn't exist already."""
        if not self.local_copy_exists():
            self.create_local_copy()

    @classmethod
    def create_local_copy_for_all_shows(cls, gen, quiet: bool = False, overwrite: bool = False):
        """
        Create a local copy of each show's image.

        Args:
            gen: An instance of PodcastFeedGenerator (from generator.generate_feed), which is used to get list of shows
                and populate their metadata.
            quiet: Set to true to disable progress messages. Warnings and errors will still be printed.
            overwrite: Set to true to ignore existing local copies; thus all images will be regenerated.
        """
        show_source = gen.show_source
        shows = show_source.shows.values()
        for show in shows:
            gen.populate_show_metadata(show, False)

        selected_images = [(show, LocalImage(show.image)) for show in shows if show.image]
        if overwrite:
            pass
        else:
            selected_images = [(show, image) for show, image in selected_images if not image.local_copy_exists()]
        cls.create_local_copy_for_shows(selected_images, quiet)

    @classmethod
    def create_local_copy_for_all_shows_with_episodes(cls, gen, quiet: bool = False, overwrite: bool = False):
        """
        Create a local copy of each show's image, if the show has published episodes.

        Args:
            gen: An instance of PodcastFeedGenerator (from generator.generate_feed), which is used to get list of shows
                and populate their metadata and check whether there are episodes.
            quiet: Set to true to disable progress messages. Warnigns and errors will still be printed.
            overwrite: Set to true to ignore existing local copies; thus all images will be regenerated.
        """
        show_source = gen.show_source
        shows = show_source.shows.values()
        for show in shows:
            gen.populate_show_metadata(show, False)

        episode_source = gen.episode_source
        episode_source.populate_all_episodes_list()

        selected_images = list()
        for show in shows:
            if not show.image:
                continue
            try:
                episode_source.episode_list(show)
            except NoEpisodesError:
                continue

            selected_images.append((show, LocalImage(show.image)))

        if not overwrite:
            selected_images = [(show, image) for show, image in selected_images if not image.local_copy_exists()]

        cls.create_local_copy_for_shows(selected_images, quiet)

    @staticmethod
    def create_local_copy_for_shows(show_image_tuples, quiet):
        """
        Create a local copy of the image for each provided show.

        Args:
            show_image_tuples: List of tuples consisting of a show and its LocalImage instance.
            quiet: Set to true to disable progress messages. Warnings and errors will still be printed.
        """
        num_images = len(show_image_tuples)

        if not num_images:
            logger.info("There are no images to process.")
            return

        logger.info("Creating local copies of %s images.", num_images)

        for item in progress.bar(show_image_tuples,
                                 hide=True if quiet else None):
            show, image = item
            logger.debug("Processing image for %(show)s", {"show": show.name})
            try:
                image.create_local_copy()
            except (IOError, ImageIsTooSmall, RuntimeError):
                logger.exception("An error happened while processing the image "
                                 "for %(show)s (image URL: %(url)s).",
                                 {"show": show.name, "url": show.image})


class ReplaceImageURL(ShowMetadataSource):
    """A metadata source for shows, which replaces its image with a properly sized local image, if it exists."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def accepts(self, show) -> bool:
        return super().accepts(show) and show.image

    def populate(self, show) -> None:
        show.image = LocalImage(show.image).get_image_url()
