import os
import json
import argparse

import pytest

from maggot.experiment import Experiment
from maggot.config import Config


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


def test_experiment_initialization_with_custom_name(nested_dict_config, tmpdir):

    experiments_dir = tmpdir.join("experiments").strpath

    experiment = Experiment(
        nested_dict_config,
        experiments_dir=experiments_dir,
        experiment_name="custom"
    )

    assert os.path.isdir(os.path.join(experiments_dir, "custom"))
    assert os.path.isfile(os.path.join(experiments_dir, "custom", "config.json"))


def test_experiment_restoration(nested_dict_config, tmpdir):

    experiments_dir = tmpdir.join("experiments").strpath

    # create an experiment
    experiment = Experiment(
        nested_dict_config, experiments_dir=experiments_dir
    )
    experiment.register_directory("temp")

    with pytest.raises(ValueError):
        # since the experiment with the same identifier has been
        # already created, experiment raises an error
        experiment = Experiment(
           nested_dict_config, experiments_dir=experiments_dir
        )

    # test restoration from identifier
    experiment = Experiment(
        resume_from=experiment.config.identifier,
        experiments_dir=experiments_dir
    )

    assert experiment.config.to_dict() == nested_dict_config
    # test that `temp` is registered after restoration
    assert os.path.isdir(experiment.temp)

    # test restoration from directory
    experiment = Experiment(
        resume_from=os.path.join(experiments_dir, experiment.config.identifier)
    )

    assert experiment.config.to_dict() == nested_dict_config
    # test that `temp` is registered after restoration
    assert os.path.isdir(experiment.temp)


def test_experiment_logging(nested_dict_config, tmpdir):

    experiments_dir = tmpdir.join("experiments").strpath

    with Experiment(
            nested_dict_config,
            experiments_dir=experiments_dir
        ) as experiment:

        print("test")

    with open(experiment.log_file, "r") as f:
        assert f.readlines()[-1].strip() == "test"

    print("test2")
    # check that nothing is logged when print is called
    # outside with block
    with open(experiment.log_file, "r") as f:
        assert f.readlines()[-1].strip() == "test"


def test_experiment_commit_hash_saving(nested_dict_config, tmpdir):

    experiments_dir = tmpdir.join("experiments").strpath

    experiment = Experiment(
        nested_dict_config, experiments_dir=experiments_dir
    )

    assert os.path.isfile(
        os.path.join(
            experiment.experiment_dir, "commit_hash"
        )
    )


def test_experiment_register_directory(nested_dict_config, tmpdir):

    experiments_dir = tmpdir.join("experiments").strpath

    experiment = Experiment(
        nested_dict_config, experiments_dir=experiments_dir
    )

    experiment.register_directory("temp")
    target = os.path.join(experiment.experiment_dir, "temp")

    assert os.path.isdir(target)
    assert experiment.temp == target


def test_experiment_register_result(simple_dict_config, tmpdir):

    experiments_dir = tmpdir.join("experiments").strpath

    experiment = Experiment(
        simple_dict_config, experiments_dir=experiments_dir
    )

    experiment.register_result("fold1.accuracy", 0.97)
    experiment.register_result("fold2.accuracy", 0.99)
    experiment.register_result("fold1.loss", 0.03)
    experiment.register_result("fold2.loss", 0.01)
    experiment.register_result("overall_accuracy", 0.98)

    results = experiment.results.to_dict()

    assert results["fold1"]["accuracy"] == 0.97
    assert results["fold2"]["accuracy"] == 0.99
    assert results["fold1"]["loss"] == 0.03
    assert results["fold2"]["loss"] == 0.01
    assert results["overall_accuracy"] == 0.98
