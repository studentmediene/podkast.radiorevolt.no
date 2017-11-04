from os.path import dirname, basename, isfile, join
from itertools import filterfalse
import glob


def find_modules(filepath):
    """
    Get list of modules which can be imported from given filepath.

    The __init__.py module and any other module starting with underscore will
    not be included.

    Args:
        filepath: Path to __init__.py file to find submodules of.

    Returns:
        Iterator with modules which can be imported from filepath, given as
        relative module paths.
    """
    modules = glob.glob(join(dirname(filepath), "*.py"))
    modules = filter(isfile, modules)
    modules = map(basename, modules)
    modules = filterfalse(lambda f: f == "__init__.py", modules)
    modules = filterfalse(lambda f: f.startswith("_"), modules)
    modules = map(lambda f: f[:-3], modules)
    modules = map(lambda f: "." + f, modules)
    return modules
