import os
import sys
import subprocess
import datetime
import shutil
import time
import json

from maggot.config import Config
from maggot.containers import NestedContainer
from maggot.utils import red


def is_same_directory(first, second):
    return os.path.realpath(first) == os.path.realpath(second)


class IfExistsModes:
    MODE_PROMPT = "prompt"
    MODE_EXIT = "exit"
    POSSIBLE_MODES = (MODE_PROMPT, MODE_EXIT)


class IfExistsResponses:
    RESPONSE_EXIT = "exit"
    RESPONSE_DELETE = "delete"
    RESPONSE_CONTINUE = "continue"
    POSSIBLE_RESPONSES = (RESPONSE_EXIT, RESPONSE_DELETE, RESPONSE_CONTINUE)


def if_exists_query(experiment_dir):

    question = (
        "Experiment {experiment_dir} already exists. You can either: \n\n"
        "  * Stop the current run and manually remove or rename the old experiment.\n"
        "  * Agree to delete the old experiment (be careful with that) and continue the run.\n"
        "  * Just continue executing the current script. This option is not recommended\n"
        "    as it could overwrite data in the existing experiment directory."
        .format(experiment_dir=experiment_dir)
    )
    prompt = (
        "[exit/delete/continue]? Type in the desired option or "
        "simply press [ENTER] to exit."
    )

    print(question)

    while True:
        print()
        print(prompt)
        choice = input().lower()
        if choice == "":
            return "exit"
        elif choice in IfExistsResponses.POSSIBLE_RESPONSES:
            return choice
        else:
            print(
                "Please respond with some from {responses}"
                .format(responses=IfExistsResponses.POSSIBLE_RESPONSES)
            )


class Experiment:

    def __init__(
        self,
        config=None,
        resume_from=None,
        experiments_dir="experiments",
        experiment_name=None,
        if_exists_mode=IfExistsModes.MODE_PROMPT,
        add_date=False
    ):
        """
        Create a new Experiment instance.

        Args:
            config:
                Can be either a path to existing JSON file,
                a dict, or an instance of mag.config.Config.
            resume_from:
                A path to an existing experiment to restore the experiment
                from.
            experiments_dir: str
                A directory for storing all experiments.
            experiment_name: str
                A custom experiment name that is used instead of one
                generated from config parameters.
            if_exists_mode: str, one of "prompt", "exit", "continue"
                Defines behavior in case experiment with the same name
                already exists. The `prompt` option will prompt user with a question,
                `exit` will simply print an error message and then
                exit the script.
            add_date: bool
                If given, appends current date str to beginning of the experiment name.
        """

        self._custom_experiment_name = experiment_name
        self.experiments_dir = experiments_dir
        self._add_date = add_date
        self._date_string = self._make_date_string()

        config_provided = config is not None
        resume_from_provided = resume_from is not None

        if not config_provided ^ resume_from_provided:
            raise ValueError(
                "Either a config or path to an existing experiment should "
                "be specified."
            )

        elif config_provided:
            self.config = self._make_config(config)

            exist_ok = False

            if self.exists and if_exists_mode == IfExistsModes.MODE_PROMPT:
                response = if_exists_query(self.experiment_dir)
                if response == IfExistsResponses.RESPONSE_EXIT:
                    self._exit()
                elif response == IfExistsResponses.RESPONSE_DELETE:
                    self._delete_experiment()
                elif response == IfExistsResponses.RESPONSE_CONTINUE:
                    exist_ok = True

            elif self.exists and if_exists_mode == IfExistsModes.MODE_EXIT:
                self._exit(
                    "Experiment {experiment_dir} already exists, exiting.".
                    format(experiments_dir=self.experiment_dir)
                )

            self._makedir(exist_ok)
            self._make_maggot_meta_dir(exist_ok)
            self._save_config()
            self._save_git_commit_hash()
            self._save_command()
            self._save_environ()

        elif resume_from_provided:

            if self.is_experiment(resume_from):
                experiments_dir, experiment_name = self._split_experiment_dir(resume_from)
                self.experiments_dir = experiments_dir
                self._custom_experiment_name = experiment_name

            self.config = Config.from_json(self._config_file)

        self._setup_log_file()

    @staticmethod
    def is_experiment(directory):

        exists = os.path.isdir(directory)
        if not exists:
            return False

        maggot_meta_exists = os.path.isdir(os.path.join(directory, ".maggot"))
        return maggot_meta_exists

    def _exit(self, message=None):
        if message is not None:
            print()
            print(message)
        sys.exit()

    def _delete_experiment(self):
        shutil.rmtree(self.experiment_dir)

    def _make_config(self, config):
        if isinstance(config, str) and os.path.isfile(config):
            return Config.from_json(config)
        elif isinstance(config, dict):
            return Config.from_dict(config)
        elif isinstance(config, Config):
            return config
        else:
            raise ValueError(
                "`config` should be either a path to JSON file, "
                "a dictonary, or an instance of mag.config.Config"
            )

    def _make_date_string(self):
        return time.strftime("%Y-%m-%d-", time.gmtime())

    def _makedir(self, exist_ok=False):
        os.makedirs(self.experiment_dir, exist_ok=exist_ok)

    def _make_maggot_meta_dir(self, exist_ok=False):
        os.makedirs(self._maggot_meta_dir, exist_ok=exist_ok)

    def _save_config(self):
        self.config.to_json(self._config_file)

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

        with open(self._git_hash_file, "w") as f:
            f.write(label.strip().decode())

    def _split_experiment_dir(self, experiment_directory):
        experiment_directory = experiment_directory.rstrip("/")
        experiments_dir, experiment_name = os.path.split(experiment_directory)
        return experiments_dir, experiment_name

    @property
    def _maggot_meta_dir(self):
        return os.path.join(self.experiment_dir, ".maggot")

    @property
    def experiment_dir(self):
        prefix = self._date_string if self._add_date else ""
        experiment_name = self._custom_experiment_name or self.config.identifier
        return os.path.join(self.experiments_dir, prefix + experiment_name)

    @property
    def exists(self):
        return os.path.isdir(self.experiment_dir)

    @property
    def _config_file(self):
        return os.path.join(self._maggot_meta_dir, "config.json")

    def _setup_log_file(self):
        logdir = os.path.join(self._maggot_meta_dir, "logs")
        os.makedirs(logdir, exist_ok=True)
        logfile = time.strftime("%Y-%m-%d-%H-%M-%S-%s", time.gmtime())
        logfile = os.path.join(logdir, logfile)
        self._logfile = logfile

    @property
    def logfile(self):
        return self._logfile

    @property
    def _git_hash_file(self):
        return os.path.join(self._maggot_meta_dir, "commit_hash")

    @property
    def _results_file(self):
        return os.path.join(self._maggot_meta_dir, "results.json")

    @property
    def _command_file(self):
        return os.path.join(self._maggot_meta_dir, "command")

    @property
    def _environ_file(self):
        return os.path.join(self._maggot_meta_dir, "environ")

    def _save_command(self):
        with open(self._command_file, "w") as fp:
            fp.write(" ".join(sys.argv) + "\n")

    def _save_environ(self):
        with open(self._environ_file, "w") as fp:
            json.dump(dict(os.environ), fp, indent=4)

    @property
    def _registered_directories_file(self):
        return os.path.join(self._maggot_meta_dir, "registered_directories")

    @property
    def directories(self):
        with open(self._registered_directories_file, "r") as fp:
            directories = [d.rstrip("\n") for d in fp.readlines()]

        def _join(d):
            return os.path.join(self.experiment_dir, d)

        return NestedContainer.from_dict({d: _join(d) for d in directories})

    def register_directory(self, dirname):
        directory = os.path.join(self.experiment_dir, dirname)
        os.makedirs(directory, exist_ok=True)

        with open(self._registered_directories_file, "a+") as fp:
            fp.write(dirname)
            fp.write("\n")

    def register_result(self, name, value):
        if os.path.exists(self._results_file):
            results = Config.from_json(self._results_file).as_flat_dict()
        else:
            results = dict()
        results[name] = value
        Config.from_flat_dict(results).to_json(self._results_file)

    @property
    def results(self):
        return Config.from_json(self._results_file)

    def __enter__(self):
        self.tee = Tee(self.logfile, "a+")
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
