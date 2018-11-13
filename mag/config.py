import os

import json
from collections import OrderedDict


class Config:
    """Config is a recursive structure that resembles JSON or nested
    dictionary, but where attributes can be accessed directly by
    repeatition of `.` operator.
    """

    @classmethod
    def from_json(cls, filepath):
        """Same as `from_dict`, but takes json file as input"""

        with open(filepath, "r") as f:
            config = json.load(f)

        return cls.from_dict(config)

    def to_json(self, filepath):
        """Saves config as JSON file"""

        dirname = os.path.dirname(filepath)
        os.makedirs(dirname, exist_ok=True)

        with open(filepath, "w") as f:
            config = json.dump(self.to_dict(), f, indent=4, sort_keys=True)

    @classmethod
    def from_dict(cls, config):
        """Recursively create Config instance from dictionary"""

        if len(config) == 0:
            raise ValueError("Config is empty")

        _config = cls()

        for name, attr in config.items():
            if not isinstance(attr, dict):
                setattr(_config, name, attr)
            else:
                setattr(_config, name, Config.from_dict(attr))

        return _config

    def to_dict(self):
        """Recursively create dict from Config"""

        dict_config = dict()

        def _copy_fields(config, dict_config):

            for name, attr in config.__dict__.items():
                if not isinstance(attr, Config):
                    dict_config[name] = attr
                else:
                    dict_config[name] = dict()
                    _copy_fields(attr, dict_config[name])

        _copy_fields(self, dict_config)

        return dict_config

    def as_flat_dict(self):
        """Returns an OrderedDict with mapping (full_parameter_name -> attr)

        Example:

        >>> config = dict(a=10, b=dict(c=20))
        >>> config = Config.from_dict(config)
        >>> config.as_flat_dict()
        OrderedDict([('a', 10), ('b.c', 20)])

        """

        parameters = OrderedDict()

        def _collect(config, prefix):
            """Recursively collect parameters from all configs for the
            current config"""

            # sort __dict__ for reproducibility
            fields = config.__dict__
            keylist = list(fields.keys())
            keylist.sort()
            sorted_fields = OrderedDict((k, fields[k]) for k in keylist)

            for name, attr in sorted_fields.items():
                full_name = ".".join((prefix, name)) if prefix else name
                if isinstance(attr, Config):
                    _collect(attr, full_name)
                else:
                    parameters[full_name] = attr

        _collect(self, "")

        return parameters

    @classmethod
    def from_flat_dict(cls, flat_dict):
        """Returns Config instance from flat dictionary.

        Example:

        >>> config = {"a.a": 10, "b": "b"}
        >>> config = Config.from_flat_dict(config)
        >>> config.as_flat_dict()
        OrderedDict([('a.a', 10), ('b', 'b')])

        """

        config = dict()

        def _fill(config, flat):

            for name, value in flat.items():
                if "." in name:
                    prefix, *suffix = name.split(".")
                    if prefix not in config:
                        config[prefix] = dict()
                    _fill(config[prefix], {".".join(suffix): value})
                else:
                    config[name] = value

        _fill(config, flat_dict)

        return cls.from_dict(config)

    @property
    def identifier(self):
        """Maps config parameters into a single string that shortly
        summarrizes the content of config`s fields. Fields a sorted
        to provide deterministic output.

        Example:

        >>> config = dict(a=10, b=dict(c=20))
        >>> config = Config.from_dict(config)
        >>> config.identifier
        '10|20'

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

        return "|".join(parameters.values())

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=4)


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