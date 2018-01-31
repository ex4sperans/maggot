import json
from collections import OrderedDict


class Config:

    @classmethod
    def from_json(cls, file):
        """Same as `from_dict`, but takes json file as input"""

        with open(file, "r") as f:
            config = json.load(f)

        return cls.from_dict(config)

    @classmethod
    def from_dict(cls, config):
        """Recursively create Config instance from dictionary"""

        _config = cls()

        for name, attr in config.items():
            if not isinstance(attr, dict):
                setattr(_config, name, attr)
            else:
                setattr(_config, name, Config.from_dict(attr))

        return _config

    def as_flat_dict(self):
        """Returns an OrderedDict with mapping (full_parameter_name -> attr)"""

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

    @property
    def identifier(self):

        parameters = self.as_flat_dict()

        def sort_key(item):
            name, attr = item
            *prefix, base = name.split(".")
            return base

        # convert values to strings
        parameters = OrderedDict((k, value_to_string(v, k))
                                 for k, v in parameters.items())
        # discard parameters that start with underscore
        # by convention, they are considered as `non-descriptive`
        # i.e. not used in the identifier
        parameters = OrderedDict((k, v) for k, v in parameters.items()
                                    if not k.startswith("_"))

        return "|".join(parameters.values())


def value_to_string(value, name):
    """Translates values (e.g. lists, ints, booleans) to strings"""

    if isinstance(value, list):
        return "x".join(map(str, value))
    if isinstance(value, bool):
        return name if value else "no_" + name
    else:
        return str(value)