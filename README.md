**maggot** is a very simple but useful library with primary goal to remove the need of custom experiment tracking approaches most people typically use. The focus is on reproducibility and removing boilerplate code.

Main issues **maggot** (at least partially) solves:

* Removes the need of meditations on what is a proper name for the experiment. Say you are a machine learning researcher/engineer and you want to train a convolutional neural network with a particular set of parameters, say, 50 convolutional layers, dropout 0.5 and relu activations. You might want to create a separate directory for this experiment to store some checkpoints and summaries there. If you do not expect to have a lot of different models you can simply go off with something like "convnet50layers" or "convnet50relu". But if the number of experiments grows, you clearly need some more reliable and automated solution. **maggot** offers such a solution, so any experiment you run will have a name derived from the parameters of your model. For the mentioned model it would be "50-relu-0.5".
* Assists reproducibility. Ever experienced situation when results you got a month ago with an "old" model are no longer reproducible? Even if you are using git, you probably have used some command line arguments that are now lost somewhere in the bash history... **maggot** stores all command line parameters in a file and duplicates the stdout to an another file. Additionaly, it saves exact git commit hash so you can easily checkout to it later and run the same code with the same parameters.
* Restoring a model is now really painless! Since **maggot** saves all the parameters you used to run the experiment, all you need to restore a model is to provide a path to a saved experiment.

Let's consider a toy example and train an SVM on Iris dataset.

First, import required packages and define command line arguments:

``` python

import argparse
import os
import pickle

from sklearn.datasets import load_iris
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score, StratifiedKFold
from mag.experiment import Experiment

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
```
Define a configuration object for the experiment:

``` python

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
```

The `random_seed` parameter is not really important for analyzing and comparing different experiments, so we included an underscore before its name in config. This tells **maggot** to ignore it for experiment's identifier (short name).

Lets create an experiment object!

``` python
experiment = Experiment(config=svm_config)
```

From here you can reach the model identifier:

```
>>> experiment.config.identifier
5-1.0-0.01
```

Or the experiment directory:

```
>>> experiment.experiment_dir
./experiments/5-1.0-0.01
```

Lets examine what this directory contains by now.

```
tree experiments/5-1.0-0.01/

├── command
├── config.json
└── log
```

`command` file contains the command we run from terminal, `config.json` stores the same configuration we used to run the experiment and `log` file will store any stdout we see during the experiment.

Lets train the model!

``` python
with experiment:

    config = experiment.config

    model = SVC(C=config.model.C, gamma=config.model.gamma)

    score = cross_val_score(
        model, X=iris.data, y=iris.target, scoring="accuracy",
        cv=StratifiedKFold(
            config.crossval.n_folds,
            shuffle=True,
            random_state=config.crossval._random_seed),
    ).mean()
```

Note that we can reach parameters using dot notation rather than `["keyword"]` notation, which looks much nicer.

We can print accuracy and this will be stored in a log file:

```python
print("Accuracy is", round(score, 4))
```

Additionaly it's possible to register `score` as a result of this experiment:

```python
experiment.register_result("accuracy", score)
```

This creates `results.json` file in experiment directory with the following content:

```
{
    "accuracy": 0.9333333333333332
}
```

Later we can use such files from different experiments to be able to compare them.

Finally, lets save the model using **pickle** module.

```python
with open(os.path.join(experiment.experiment_dir, "model.pkl"), "wb") as f:
    pickle.dump(model, f)
```

See how directory structure has changed:

```
├── command
├── config.json
├── log
├── model.pkl
└── results.json
```

If we want to restore the experiment we can easily do:

```python
with Experiment(resume_from="experiments/5-1.0-0.01") as experiment:
    config = experiment.config    # the same config we created on the training phase
    ...
```

Configuration file and other related stuff will be loaded automatically.

We can easily run several experiments with different parameters:

```
python ../maggot/examples/iris_sklearn.py --C=10
python ../maggot/examples/iris_sklearn.py --C=10 --gamma=1
python ../maggot/examples/iris_sklearn.py --C=10 --gamma=0.1
python ../maggot/examples/iris_sklearn.py --C=0.001 --gamma=0.1
python ../maggot/examples/iris_sklearn.py --C=0.001 --gamma=10
```

And easily compare them now:

```
python -m maggot.summarize experiments --metrics=accuracy

Results for experiments:

              accuracy
5-0.001-10.0  0.793333
5-0.001-0.1   0.933333
5-1.0-0.01    0.933333
5-10.0-0.1    0.980000
5-10.0-0.01   0.966667
5-10.0-1.0    0.960000
```

Various other options are available and will be documented soon.

**Installation**

To install, clone the repository and then use ```pip install .``` or run ```pip install git+https://github.com/ex4sperans/maggot.git``` to install directly from GitHub. The repository will be added to PyPI soon to simplify the installation.
