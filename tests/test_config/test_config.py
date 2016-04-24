import os
import configparser

import pytest

import kbb


def test_config_default():
    k = kbb.Kbb()
    config = dict()
    config_path = os.path.join(os.getcwd(), 'tests/test_config')
    k._load_config(config_path, config, 'config')

    assert config['SyncRate']  == 60
    assert config['stages'] == ['todo', 'doing', 'done']


def test_config_no_stage():
    k = kbb.Kbb()
    config = dict()
    config_path = os.path.join(os.getcwd(), 'tests/test_config')
    k._load_config(config_path, config, 'config2')

    assert config['SyncRate']  == 60
    assert config['stages'] == []


def test_config_broken_parse():
    k = kbb.Kbb()
    config = dict()
    config_path = os.path.join(os.getcwd(), 'tests/test_config')

    with pytest.raises(configparser.ParsingError):
        k._load_config(config_path, config, 'config3')


def test_config_missing_required_section():
    k = kbb.Kbb()
    config = dict()
    config_path = os.path.join(os.getcwd(), 'tests/test_config')

    with pytest.raises(KeyError):
        k._load_config(config_path, config, 'config4')
