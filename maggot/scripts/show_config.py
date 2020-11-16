import argparse
import os
import sys
from collections import defaultdict

import pandas as pd

from maggot import Experiment
from maggot.utils import bold


def collect_args(args):

    parser = argparse.ArgumentParser(
        prog="show-config",
        description=bold("Show config used in a particular experiment."),
        usage=("maggot show-config EXPERIMENT"),
    )

    parser.add_argument(
        "experiment", type=str, nargs="?",
        help="Experiment to show config for."
    )

    args = parser.parse_args(args)

    if args.experiment is None:
        parser.print_help()
        sys.exit()

    return args


def main(args=None):

    args = collect_args(args)
    experiment = Experiment(resume_from=args.experiment)
    print(experiment.config)

if __name__ == "__main__":
    main()
