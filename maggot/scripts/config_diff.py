import argparse
import os
import sys
from collections import defaultdict

import pandas as pd

from maggot import Experiment
from maggot.utils import bold
from maggot.diffs import colorful_config_diff


def collect_args(args):

    parser = argparse.ArgumentParser(
        prog="config-diff",
        description=bold("Show diff between configs in two experiments."),
        usage=("maggot config-diff EXPERIMENT1 EXPERIMENT2"),
    )

    parser.add_argument(
        "first", type=str, nargs="?",
        help="First experiment."
    )
    parser.add_argument(
        "second", type=str, nargs="?",
        help="Second experiment."
    )

    args = parser.parse_args(args)

    if args.first is None or args.second is None:
        parser.print_help()
        sys.exit()

    return args


def main(args=None):

    args = collect_args(args)
    first = Experiment(resume_from=args.first)
    second = Experiment(resume_from=args.second)

    print("First:", bold(first.experiment_dir))
    print("Second:", bold(second.experiment_dir))
    print()
    diff = colorful_config_diff(first.config, second.config)
    print(diff)


if __name__ == "__main__":
    main()
