from show_processors.set_defaults import SetDefaults


class ForceValues(SetDefaults):
    """
    Override values set so far with values from this processor's settings.

    The accepted settings are the same as for SetDefaults. Leave a setting
    out in order to not override it, or set it to a falsy value (None for
    explicit).
    """
    @staticmethod
    def _set_if_false(show, attribute, default_value):
        # Replace the if-false check with True, so we always set
        if default_value:
            setattr(show, attribute, default_value)

    @staticmethod
    def _set_if_none(show, attribute, default_value):
        # Replace the if-none check with True, so we always set
        if default_value is not None:
            setattr(show, attribute, default_value)
