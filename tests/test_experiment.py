import os
import json

import pytest

from mag.experiment import Experiment
from mag.config import Config


@pytest.fixture
def simple_dict_config():

    config = dict(
        a=10,
        b=[1, 2, 3],
        c="a"
    )

    return config


@pytest.fixture
def nested_dict_config(simple_dict_config):

    config = dict(
        a=10,
        _b="a",
        c=simple_dict_config
    )

    return config


def test_experiment_initialization(nested_dict_config, tmpdir):

    experiments_dir = tmpdir.join("experiments").strpath

    experiment = Experiment(
        nested_dict_config, experiments_dir=experiments_dir
    )

    config = Config.from_json(os.path.join(
        experiments_dir, experiment.config.identifier, "config.json")
    )

    assert config.to_dict() == nested_dict_config


def test_experiment_restoration(nested_dict_config, tmpdir):

    experiments_dir = tmpdir.join("experiments").strpath

    # create an experiment
    experiment = Experiment(
        nested_dict_config, experiments_dir=experiments_dir
    )

    with pytest.raises(ValueError):
        # since the experiment with the same identifier has been
        # already created, experiment raises an error
        experiment = Experiment(
           nested_dict_config, experiments_dir=experiments_dir
        )

    # test restoration
    experiment = Experiment(
        resume_from=experiment.config.identifier,
        experiments_dir=experiments_dir
    )

    assert experiment.config.to_dict() == nested_dict_config


def test_experiment_logging(nested_dict_config, tmpdir):

    experiments_dir = tmpdir.join("experiments").strpath

    with Experiment(
            nested_dict_config,
            experiments_dir=experiments_dir
        ) as experiment:

        print("test")

    with open(experiment.log_file, "r") as f:
        assert f.read().strip() == "test"

    print("test2")
    # check that nothing is logged when print is called
    # outside with block
    with open(experiment.log_file, "r") as f:
        assert f.read().strip() == "test"


def test_experiment_commit_hash_saving(nested_dict_config, tmpdir):

    experiments_dir = tmpdir.join("experiments").strpath

    experiment = Experiment(
        nested_dict_config, experiments_dir=experiments_dir
    )

    assert os.path.isfile(os.path.join(
        experiment.experiment_dir, "commit_hash")
    )