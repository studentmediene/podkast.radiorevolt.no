import collections
import copy


__all__ = ["deep_update"]


def deep_update(orig_dict, other, allow_new: bool=False):
    """Create copy of orig_dict with values overwritten by those in other.

    Values are updated in a deep manner, which means that dictionaries in
    orig_dict are not replaced in their entirety by those in other; instead,
    the update procedure is done recursively so that you need not redefine all
    values of a dictionary inside other just so you can change one value in
    that dictionary in orig_dict.

    Args:
        orig_dict: Original dictionary to start with.
        other: Dictionary which should overwrite values in orig_dict.
        allow_new: Boolean which determines whether a key in other which is not
            found in orig_dict should result in a ValueError (False, the
            default) or be set without error (True).

    Returns:
        A new dictionary where values found in other use their value from other,
        while others use the existing value from orig_dict.
    """
    # Don't change the existing dictionary (since we return the result)
    orig_dict = copy.copy(orig_dict)
    # For each key-item pair to update
    for key, value in other.items():
        # Do we need to run advanced update procedure?
        new_is_mapping = isinstance(value, collections.Mapping)
        old_is_mapping_if_exists = isinstance(
            orig_dict.get(key, {}),
            collections.Mapping
        )
        old_exists = key in orig_dict
        if new_is_mapping and old_exists and old_is_mapping_if_exists:
            orig_dict[key] = deep_update(orig_dict[key], value, allow_new)
        else:
            if not allow_new and not old_exists:
                raise ValueError(
                    "Key {!r} in other dictionary was not found in the "
                    "original dictionary. It is likely spelled wrong or is "
                    "incorrect. (Set allow_new to True if the intent was to "
                    "allow setting new values.)".format(key))
            else:
                orig_dict[key] = value
    return orig_dict
