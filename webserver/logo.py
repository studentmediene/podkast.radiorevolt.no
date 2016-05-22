import os.path
from urllib.parse import urlparse, unquote
from flask import url_for
from PIL import Image
import requests
import io
import tempfile
from warnings import warn
import warnings
from generator.metadata_sources.show_metadata_source import ShowMetadataSource
import sys
import traceback


class ImageIsTooSmall(UserWarning):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


image_directory = os.path.join(os.path.dirname(__file__), "static", "images")
# Assuming square image sizes
min_image_size = 1400
max_image_size = 3000

warnings.simplefilter('error', Image.DecompressionBombWarning)


def _get_filename(original_url):
    """Get the filename part of the provided url."""
    return os.path.splitext(os.path.basename(unquote(urlparse(original_url).path)))[0] + ".png"


def _path_to_local_copy(filename):
    """Get the absolute path to the image with the given filename. It need not exist yet."""
    return os.path.join(image_directory, filename)


def get_image_url(original_url):
    """Get the absolute URL which is to be used for the given original image URL.

    If a local copy exists for this image, the url for that is returned. If it does not, the original url is returned
    untouched.
    """
    filename = _get_filename(original_url)
    if _local_copy_exists(filename):
        return _get_url_for_image(filename)
    else:
        return original_url


def _get_url_for_image(filename):
    """Get the absolute URL for a local image with the given filename."""
    return url_for("static", filename=os.path.join(os.path.basename(image_directory), filename), _external=True)


def _local_copy_exists(filename):
    """Returns true if a local image with the given filename exists."""
    return os.path.exists(_path_to_local_copy(filename))


def _resize(original_image, new_image):
    """Create a properly resized image.

    Args:
          original_image: File object with the original image.
          new_image: File object in which the new, resized image is to be written.
    """
    img = Image.open(original_image)

    new_width, new_height = _calculate_new_image_size(img, min_image_size, max_image_size)
    new_img = _create_resized_image(img, new_width, new_height)
    new_img.save(new_image, "png")


def _create_resized_image(image, width, height):
    """Manipulate image so it has the given width and height."""
    # While it might look like we could have used Image.thumbnail, it is not appropriate since the image
    # might need to be upscaled
    return image.resize((width, height), Image.LANCZOS)


def _calculate_new_image_size(img: Image.Image, min_size: int, max_size: int) -> (int, int):
    """Figure out the new dimensions for the provided image.

    It will preserve aspect ratio and will be between min_size and max_size.

    Args:
        img: Image which will be inspected (to get the current dimensions).
        min_size: Minimum size for both width and height (in pixels).
        max_size: Maximum size for both width and height (in pixels).
    Raises:
        RuntimeError: When the image cannot possibly fit the requirements without altering the aspect ratio.

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
        warn(("The size of the image is {width}x{height}, which means it must be upscaled so it fits iTunes' rules "
              "(minimum {min}x{min}, maximum {max}x{max}). Upscaling always looks ugly, so please export the logo at a "
              "higher resolution or recreate it with a higher resolution in mind.")
             .format(width=width, height=height, min=min_size, max=max_size),
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


def create_local_copy(original_url):
    """Create a local, properly resized copy of the image on the given url."""
    r = requests.get(original_url)
    r.raise_for_status()
    original_image = io.BytesIO(r.content)

    # Write resized image to temporary file, before moving it to its intended location
    new_image = None
    try:
        new_image = tempfile.NamedTemporaryFile("w+b", delete=False)
        # Write to the temporary file
        _resize(original_image, new_image)
        new_image.close()
        original_image.close()
        # Overwrite the possibly existing image, as an atomic action
        os.replace(new_image.name, _path_to_local_copy(_get_filename(original_url)))
    except Exception:
        if new_image:
            os.remove(new_image.name)
        raise


def create_local_copy_if_not_exists(original_url):
    """Create a local, properly resized copy of the image on the given url, if it doesn't exist already."""
    if not _local_copy_exists(_get_filename(original_url)):
        create_local_copy(original_url)


class ReplaceImageURL(ShowMetadataSource):
    """A metadata source for shows, which replaces its image with a properly sized image, if it exists."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def accepts(self, show) -> bool:
        return super().accepts(show) and show.image

    def populate(self, show) -> None:
        show.image = get_image_url(show.image)


def create_local_copy_for_all_shows(gen, quiet: bool=False, overwrite: bool=False):
    show_source = gen.show_source
    shows = show_source.shows.values()
    for show in shows:
        gen.populate_show_metadata(show, False)

    if overwrite:
        selected_shows = [show for show in shows if show.image]
    else:
        selected_shows = [show for show in shows if show.image and not _local_copy_exists(_get_filename(show.image))]
    num_shows = len(selected_shows)

    if not num_shows:
        if not quiet:
            print("There are no images to process.", file=sys.stderr)

    if not quiet:
        def print_progress(i, show):
            print("Processing image {i:02}/{n:02}: {show.title}".format(i=i + 1, n=num_shows, show=show), file=sys.stderr)
    else:
        def print_progress(*args, **kwargs):
            pass   # no-op

    for i, show in enumerate(selected_shows):
        print_progress(i, show)
        try:
            create_local_copy(show.image)
        except (IOError, ImageIsTooSmall, RuntimeError):
            print("An error happened while processing that image. Details:", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
