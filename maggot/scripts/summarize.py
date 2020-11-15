import argparse
import os
import sys
from collections import defaultdict

import pandas as pd

from maggot import Experiment
from maggot.containers import NestedContainer
from maggot.utils import bold, green, red, blue

pd.set_option("display.max_colwidth", 500)


def collect_results(directory):

    items = os.listdir(directory)
    fullpath = os.path.abspath(directory)

    def keep_only_experiments(items):
        for item in items:
            if Experiment.is_experiment(os.path.join(fullpath, item)):
                yield item

    experiments = list(keep_only_experiments(items))

    if not experiments:
        raise ValueError("Directory contains no experiments.")

    print(bold("\nResults for {directory}:".format(directory=fullpath)))
    print()

    def results():
        for experiment in experiments:
            results_file = os.path.join(directory, experiment, ".maggot", "results.json")
            if os.path.isfile(results_file):
                result = NestedContainer.from_json(results_file)
                result = result.as_flat_dict()
                yield experiment, result

    all_metrics = set()
    for experiment, result in results():
        all_metrics.update(result)

    all_results = defaultdict(list)
    for experiment, result in results():
        all_results["experiment"].append(experiment)
        for metric in all_metrics:
            all_results[metric].append(result.get(metric, ""))

    return all_results


def stylize_results(df):

    df = df.to_string()
    header, *content = df.split("\n")
    header = bold(header)

    stylized = []
    for item in content:
        first_space = item.index(" ")
        experiment, metrics = item[:first_space], item[first_space:]
        stylized.append(bold(blue(experiment)) + bold(green(metrics)))

    df = "\n".join([header] + stylized)

    return df


def collect_args(args):

    parser = argparse.ArgumentParser(
        prog="summarize",
        description=bold("Summarize results from different experiments."),
        usage=("maggot summarize DIRECTORY ..."),
    )

    parser.add_argument(
        "directory", type=str, nargs="?",
        help="Directory to print summary for"
    )
    parser.add_argument(
        "--sort", type=str,
        help="Metric name to use as a key for sorting entries in the final dataframe."
    )
    parser.add_argument(
        "--ascending", default=False, action="store_true",
        help="Sorting direction. Used only if `sort` is given."
    )

    args = parser.parse_args(args)

    if args.directory is None:
        parser.print_help()
        sys.exit()

    return args


def main(args=None):

    args = collect_args(args)

    results = collect_results(args.directory)
    index = results.pop("experiment")
    df = pd.DataFrame(results, index=index)

    if args.sort is not None:
        df = df.sort_values(by=args.sort, ascending=args.ascending)

    print(stylize_results(df))


if __name__ == "__main__":
    main()
