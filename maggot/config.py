from collections import OrderedDict

from maggot import get_current_separator
from maggot.containers import NestedContainer


class Config(NestedContainer):

    @property
    def identifier(self):
        """
        Maps config parameters into a single string that shortly
        summarrizes the content of config`s fields. Fields a sorted
        to provide deterministic output.

        Example:

        >>> config = dict(a=10, b=dict(c=20))
        >>> config = Config.from_dict(config)
        >>> config.identifier
        '10-20'

        """

        parameters = self.as_flat_dict()

        def sort_key(item):
            name, attr = item
            *prefix, base = name.split(".")
            return base

        def is_descriptive(key):
            *prefix, base = key.split(".")
            return not base.startswith("_")

        # convert values to strings
        parameters = OrderedDict((k, value_to_string(v, k))
                                 for k, v in parameters.items())
        # discard parameters that start with underscore
        # by convention, they are considered as `non-descriptive`
        # i.e. not used in the identifier
        parameters = OrderedDict((k, v) for k, v in parameters.items()
                                 if is_descriptive(k))

        return get_current_separator().join(parameters.values())


def value_to_string(value, name):
    """Translates values (e.g. lists, ints, booleans) to strings"""

    def last(name):
        *prefix, base = name.split(".")
        return base

    if isinstance(value, list):
        return "x".join(map(str, value))
    if isinstance(value, bool):
        return last(name) if value else "no_" + last(name)
    else:
        return str(value)