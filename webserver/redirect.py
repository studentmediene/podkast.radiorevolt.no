import shortuuid
from . import settings

db = None

def noop(*args, **kwargs):
    pass

get_original_sound = noop
get_original_article = noop
get_new_sound = noop
get_new_article = noop
