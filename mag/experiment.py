import os
import shutil

from mag.config import Config


class Experiment:

    def __init__(self, config, experiments_dir="./experiments"):

        if isinstance(config, str) and os.path.isfile(config):
            self.config = Config.from_json(config)
        elif isinstance(config, dict):
            self.config = Config.from_dict(config)
        else:
            self.config = config
        
        self.experiments_dir = experiments_dir

        os.makedirs(self.experiment_dir, exist_ok=True)
        self.config.to_json(self.config_file)

    @property
    def experiment_dir(self):

        return os.path.join(self.experiments_dir, self.config.identifier)

    @property
    def config_file(self):

        return os.path.join(self.experiment_dir, "config.json")