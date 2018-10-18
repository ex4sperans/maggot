import argparse
import os
from collections import defaultdict

import pandas as pd

from mag.config import Config
from mag.utils import bold, green, red, blue

pd.set_option("display.max_colwidth", 500)


def collect_results(directory, metrics):

    experiments = os.listdir(directory)
    if experiments:
        fullpath = os.path.abspath(directory)
        print(bold("\nResults for {directory}:".format(directory=fullpath)))
        print()

    all_results = defaultdict(list)

    for experiment in experiments:
        results_file = os.path.join(directory, experiment, "results.json")
        if os.path.isfile(results_file):
            result = Config.from_json(results_file)
            result = result.as_flat_dict()
            all_results["experiment"].append(experiment)
            for metric in metrics:
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


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=bold("Summarize results from different experiments."),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "directory", type=str,
        help="directory to print summary for")
    parser.add_argument(
        "--metrics", type=str, nargs="+",
        help="Which metrics to use for summary")

    args = parser.parse_args()

    results = collect_results(args.directory, args.metrics)
    index = results.pop("experiment")
    df = pd.DataFrame(results, index=index)

    print(stylize_results(df))
