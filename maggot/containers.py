import os

import json
from collections import OrderedDict

from maggot import get_current_separator


class NestedContainer:
    """
    A recursive structure that resembles a JSON object or nested
    dictionary with a only difference that attributes can be accessed directly
    by repeatedly applying getattr() or the '.' operator.
    """

    @classmethod
    def from_json(cls, filepath):
        """Same as `from_dict`, but takes json file as input"""

        with open(filepath, "r") as f:
            nested_dict = json.load(f)

        return cls.from_dict(nested_dict)

    def to_json(self, filepath):
        """Dumps container into a JSON file"""

        dirname = os.path.dirname(filepath)
        os.makedirs(dirname, exist_ok=True)

        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=4, sort_keys=True)

    @classmethod
    def from_dict(cls, nested_dict):
        """Create a NestedContainer instance from a dictionary"""

        _base = cls()

        for name, attr in nested_dict.items():
            if not isinstance(attr, dict):
                setattr(_base, name, attr)
            else:
                setattr(_base, name, cls.from_dict(attr))

        return _base

    def to_dict(self):
        """Turn contrainer into a dict."""

        nested_dict = dict()

        def _copy_fields(container, data):
            for name, attr in container.__dict__.items():
                if not isinstance(attr, NestedContainer):
                    data[name] = attr
                else:
                    data[name] = dict()
                    _copy_fields(attr, data[name])

        _copy_fields(self, nested_dict)

        return nested_dict

    def as_flat_dict(self):
        """Returns an OrderedDict with mapping (full_parameter_name -> attr)

        Example:

        >>> nested_dict = dict(a=10, b=dict(c=20))
        >>> container = NestedContainer.from_dict(nested_dict)
        >>> container.as_flat_dict()
        OrderedDict([('a', 10), ('b.c', 20)])

        """

        parameters = OrderedDict()

        def _collect(container, prefix):
            """
            Recursively collect parameters from all subcontainers for the
            current container.
            """

            # sort __dict__ for reproducibility
            fields = container.__dict__
            keylist = sorted(fields)
            sorted_fields = OrderedDict((k, fields[k]) for k in keylist)

            for name, attr in sorted_fields.items():
                full_name = ".".join((prefix, name)) if prefix else name
                if isinstance(attr, NestedContainer):
                    _collect(attr, full_name)
                else:
                    parameters[full_name] = attr

        _collect(self, "")

        return parameters

    @classmethod
    def from_flat_dict(cls, flat_dict):
        """
        Creates a NestedContainer instance from a flat dict.

        Example:

        >>> flat_dict = {"a.a": 10, "b": "b"}
        >>> container = NestedContainer.from_flat_dict(flat_dict)
        >>> container.as_flat_dict()
        OrderedDict([('a.a', 10), ('b', 'b')])

        """

        nested_dict = dict()

        def _fill(nested_dict, flat):

            for name, value in flat.items():
                if "." in name:
                    prefix, *suffix = name.split(".")
                    if prefix not in nested_dict:
                        nested_dict[prefix] = dict()
                    _fill(nested_dict[prefix], {".".join(suffix): value})
                else:
                    nested_dict[name] = value

        _fill(nested_dict, flat_dict)

        return cls.from_dict(nested_dict)

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=4)
