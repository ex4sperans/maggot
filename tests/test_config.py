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
        _b="a",
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
    assert config._b == "a"
    assert config.c.a == 10
    assert config.c.b == [1, 2, 3]


def test_config_to_dict(nested_dict_config):

    config = Config.from_dict(nested_dict_config)
    recovered_dict = config.to_dict()

    assert nested_dict_config == recovered_dict


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
    assert config._b == "a"
    assert config.c.a == 10
    assert config.c.b == [1, 2, 3]


def test_config_to_json(nested_dict_config, tmpdir):

    filepath = tmpdir.join("nested_dict_config.json").strpath

    config = Config.from_dict(nested_dict_config)
    config.to_json(filepath)

    recovered_config = Config.from_json(filepath)

    assert config.to_dict() == recovered_config.to_dict()


def test_config_indentifier(nested_dict_config):

    config = Config.from_dict(nested_dict_config)

    # identifier should be sorted as follows:
    # a, c.a, c.b, c.c
    assert config.identifier == "10|10|1x2x3|a"