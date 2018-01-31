

class Config:

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
        """Returns a dict with mapping (full_parameter_name -> attr)"""

        parameters = dict()

        def _collect(config, prefix):
            """Recursively collect parameters from all configs for
            current config"""

            for name, attr in config.__dict__.items():
                full_name = ".".join((prefix, name)) if prefix else name
                if isinstance(attr, Config):
                    _collect(attr, full_name)
                else:
                    parameters[full_name] = attr

        _collect(self, "")

        return parameters
