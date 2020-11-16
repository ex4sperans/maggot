import argparse
import os
import sys
from collections import defaultdict

import pandas as pd

from maggot import Experiment
from maggot.utils import bold


def collect_args(args):

    parser = argparse.ArgumentParser(
        prog="show-command",
        description=bold("Show command that was used to run a particular experiment."),
        usage=("maggot show-command EXPERIMENT"),
    )

    parser.add_argument(
        "experiment", type=str, nargs="?",
        help="Experiment to show command for."
    )

    args = parser.parse_args(args)

    if args.experiment is None:
        parser.print_help()
        sys.exit()

    return args


def main(args=None):

    args = collect_args(args)
    experiment = Experiment(resume_from=args.experiment)
    with open(experiment._command_file) as fp:
        command = fp.read().strip()
    print("[python]", command)

if __name__ == "__main__":
    main()
