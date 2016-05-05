# Utilities for migrating from Feedburner

**This utility depends on some software which does not run on Python3, so you CANNOT use the same virtualenv as the rest of the project.**

Here are setup instructions.

1. Change into this directory.

2. Install the following packages (this time assuming Fedora; how does THAT feel?):
   * python-lxml
   * PyQt4 and PyQt4-devel
   * Ubuntu-specific: libx11-dev, libxtst-dev, libpng-dev
   * Maybe some more? If you find that you must install more packages, you may take a look at the statistics repo and Setup.md. Please add the dependencies you find here.

1. Run the following:
   ```
   virtualenv -p python2.7 --system-site-packages venv
   . venv/bin/activate
   ```
   You need the `--system-site-packages` flag in order to access `PyQt4` from the virtual environment.


3. Now we can install dependencies:
   ```
   pip install -r requirements.py
   ```

4. Done!

Get `ALTERNATE_SHOW_NAMES`
------------------------

Run `get_urls.py`, redirecting the output to a temporary file, and follow the instructions.


Get `generator/metadata_sources/show/manual_changes.json`
---------------------------------------------------------

Run `get_categories.py`, redirecting the output to a temporary file, and follow the instructions.
