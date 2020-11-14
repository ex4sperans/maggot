import argparse
import os
import pickle

from sklearn.datasets import load_iris
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score, StratifiedKFold
from maggot.experiment import Experiment


parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    "--C", type=float, default=1.0,
    help="Regularization parameter for SVM")
parser.add_argument(
    "--gamma", type=float, default=0.01,
    help="Kernel parameter for SVM")
parser.add_argument(
    "--cv", type=int, default=5,
    help="Number of folds for cross-validation")
parser.add_argument(
    "--cv_random_seed", type=int, default=42,
    help="Random seed for cross-validation iterator")

args = parser.parse_args()

svm_config = {
    "model": {
        "C": args.C,
        "gamma": args.gamma
    },
    "crossval": {
        "n_folds": args.cv,
        "_random_seed": args.cv_random_seed
    }
}

iris = load_iris()

with Experiment(config=svm_config) as experiment:

    config = experiment.config

    model = SVC(C=config.model.C, gamma=config.model.gamma)

    score = cross_val_score(
        model, X=iris.data, y=iris.target, scoring="accuracy",
        cv=StratifiedKFold(
            config.crossval.n_folds,
            shuffle=True,
            random_state=config.crossval._random_seed),
    ).mean()

    print("Accuracy is", round(score, 4))
    experiment.register_result("accuracy", score)

    with open(os.path.join(experiment.experiment_dir, "model.pkl"), "wb") as f:
        pickle.dump(model, f)
