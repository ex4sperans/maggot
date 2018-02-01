import os
import sys
import subprocess

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

        self._makedir() 
        self._save_config()
        self._save_git_commit_hash()

    def _makedir(self):
        os.makedirs(self.experiment_dir, exist_ok=False)

    def _save_config(self):
        self.config.to_json(self.config_file)

    def _save_git_commit_hash(self):
        try:
            label = subprocess.check_output(["git", "rev-parse", "HEAD"])
        except subprocess.CalledProcessError:
            # skip this step if current directory is
            # not a git repository
            return

        with open(self.git_hash_file, "w") as f:
            f.write(label.strip().decode())
    
    @property
    def experiment_dir(self):
        return os.path.join(self.experiments_dir, self.config.identifier)

    @property
    def config_file(self):
        return os.path.join(self.experiment_dir, "config.json")

    @property
    def log_file(self):
        return os.path.join(self.experiment_dir, "log")

    @property
    def git_hash_file(self):
        return os.path.join(self.experiment_dir, "commit_hash")

    def __enter__(self):
        self.tee = Tee(self.log_file, "w")
        return self

    def __exit__(self, *args):
        self.tee.close()


class Tee:
    """A helper class to duplicate stdout to a log file"""

    def __init__(self, name, mode):
        self.file = open(name, mode)
        self.stdout = sys.stdout
        sys.stdout = self

    def close(self, *args):
        sys.stdout = self.stdout
        self.file.close()

    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)
    
    def flush(self):
        self.file.flush()