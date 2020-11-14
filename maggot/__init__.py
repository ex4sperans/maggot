DEFAULT_SEPARATOR = "-"
SEPARATOR = DEFAULT_SEPARATOR


def use_custom_separator(separator):
    global SEPARATOR
    SEPARATOR = separator


def use_default_separator():
    global SEPARATOR
    SEPARATOR = DEFAULT_SEPARATOR


def get_current_separator():
    return SEPARATOR


from maggot.experiment import Experiment
from maggot.config import Config
