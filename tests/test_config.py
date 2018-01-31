import os
import json

import pytest

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
        b="a",
        c=simple_dict_config
    )

    return config


def test_config_from_dict(simple_dict_config, nested_dict_config):

    config = Config.from_dict(simple_dict_config)

    assert config.a == 10
    assert config.b == [1, 2, 3]
    assert config.c == "a"

    config = Config.from_dict(nested_dict_config)

    assert config.a == 10
    assert config.b == "a"
    assert config.c.a == 10
    assert config.c.b == [1, 2, 3]


def test_config_as_flat_dict(nested_dict_config):

    flat_dict = Config.from_dict(nested_dict_config).as_flat_dict()

    assert flat_dict["c.a"] == 10
    assert flat_dict["c.b"] == [1, 2, 3]


def test_config_from_json(nested_dict_config, tmpdir):

    filepath = tmpdir.join("nested_dict_config.json").strpath

    with open(filepath, "w") as f:
        json.dump(nested_dict_config, f, indent=4)

    config = Config.from_json(filepath)

    assert config.a == 10
    assert config.b == "a"
    assert config.c.a == 10
    assert config.c.b == [1, 2, 3]
