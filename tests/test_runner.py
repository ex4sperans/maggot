import os
import json

import pytest


from mag.runner import Runner
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


def test_runner_initialization(nested_dict_config, tmpdir):

    experiments_dir = tmpdir.join("experiments").strpath

    runner = Runner(nested_dict_config, experiments_dir=experiments_dir)

    config = Config.from_json(os.path.join(
        experiments_dir, runner.config.identifier, "config.json")
    )

    assert config.to_dict() == nested_dict_config