import os
import sys
import subprocess
import datetime

from mag.config import Config


class Experiment:

    def __init__(self, config=None, resume_from=None,
                 logfile_name="log", experiments_dir="./experiments",
                 implicit_resuming=False):
        """Create a new Experiment instance.

        Args:
            config: can be either a path to existing JSON file,
                a dict, or an instance of mag.config.Config.
            resume_from: an identifier (str) to resume from
                the past experiment. It is important to emphasize that
                it should be indentifier of the experiment, not the full path.
                Full path is then constructed as experiments_dir / resume_from
            logfile_name: str, naming for log file. This can be useful to
                separate logs for different runs on the same experiment
            experiments_dir: str, a path where experiment will be saved
            implicit_resuming: bool, whether to allow resuming
                even if experiment already exists
        """

        self.experiments_dir = experiments_dir
        self.logfile_name = logfile_name

        if config is None and resume_from is None:
            raise ValueError(
                "If `config` argument was not passed explicitly, "
                "indentifier of existing experiment "
                "should be specified by `resume_from` argument."
            )

        elif config is not None and resume_from is None:

            if isinstance(config, str) and os.path.isfile(config):
                self.config = Config.from_json(config)
            elif isinstance(config, dict):
                self.config = Config.from_dict(config)
            elif isinstance(config, Config):
                self.config = config
            else:
                raise ValueError(
                    "`config` should be either a path to JSON file "
                    "a dictonary or an instance of mag.config.Config"
                )

            if os.path.isdir(self.experiment_dir):
                if not implicit_resuming:
                    raise ValueError(
                        "Experiment with identifier {identifier} "
                        "already exists. Set `resume_from` to the corresponding "
                        "identifier (directory name) {directory} or delete it "
                        "manually and then rerun the code.".format(
                            identifier=self.config.identifier,
                            directory=self.config.identifier
                        )
                    )
            else:
                self._makedir()
                self._save_config()
                self._save_git_commit_hash()

        elif resume_from is not None and config is None:

            self.config = Config.from_json(
                os.path.join(experiments_dir, resume_from, "config.json")
            )
            self._register_existing_directories()

        elif config is not None and resume_from is not None:

            raise ValueError(
                "`config` and `resume_from` arguments are mutually "
                "exclusive: either create new experiment (by passing only "
                "`config`) or resume from the existing experiment "
                "(by passing only `resume_from`)"
            )

    def _makedir(self):
        os.makedirs(self.experiment_dir, exist_ok=False)

    def _save_config(self):
        self.config.to_json(self.config_file)

    def _save_git_commit_hash(self):
        try:
            label = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                stderr=subprocess.PIPE
            )
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
        return os.path.join(self.experiment_dir, self.logfile_name)

    @property
    def git_hash_file(self):
        return os.path.join(self.experiment_dir, "commit_hash")

    @property
    def results_file(self):
        return os.path.join(self.experiment_dir, "results.json")

    def register_directory(self, dirname):
        directory = os.path.join(self.experiment_dir, dirname)
        os.makedirs(directory, exist_ok=True)
        setattr(self, dirname, directory)

    def _register_existing_directories(self):
        for item in os.listdir(self.experiment_dir):
            fullpath = os.path.join(self.experiment_dir, item)
            if os.path.isdir(fullpath):
                setattr(self, item, fullpath)

    def register_result(self, name, value):
        if os.path.exists(self.results_file):
            results = Config.from_json(self.results_file).as_flat_dict()
        else:
            results = dict()
        results[name] = value
        Config.from_flat_dict(results).to_json(self.results_file)

    @property
    def results(self):
        return Config.from_json(self.results_file)

    def __enter__(self):
        self.tee = Tee(self.log_file, "a+")
        return self

    def __exit__(self, *args):
        self.tee.close()


class Tee:
    """A helper class to duplicate stdout to a log file"""

    def __init__(self, name, mode):
        self.file = open(name, mode)
        self.stdout = sys.stdout
        sys.stdout = self

        self._log_time()

    def _log_time(self):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.file.write("\n")
        self.file.write(current_time)
        self.file.write("\n\n")

    def close(self, *args):
        sys.stdout = self.stdout
        self.file.close()

    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)

    def flush(self):
        self.file.flush()
