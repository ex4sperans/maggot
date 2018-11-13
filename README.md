**mag** is a very simple but useful library with primary goal to remove the need of custom experiment tracking approaches most people typically use. The focus is on reproducibility and removing boilerplate code.

Main issues **mag** (at least partially) solves:

* Removes the need of meditations on what is a proper name for the experiment. Say you are a machine learning researcher/engineer and you want to train a convolutional neural network with a particular set of parameters, say, 50 convolutional layers, dropout 0.5 and relu activations. You might want to create a separate directory for this experiment to store some checkpoints and summaries there. If you typically don't have a lot of different models you can simply go off with something like "convnet50layers" or "convnet50relu". But if the number of experiments grows you clearly need some more reliable and automated solution. **mag** offers such solution, so any experiment you run will have a name inferred from the parameters of your model. For the mentioned model it would be "50|relu|0.5".
* Assists reproducibility. Ever experienced situation when results you got a month ago with an "old" model are no longer repeatable? Even if you are using git, you probably used some command line arguments that are now lost somewhere is bash history... **mag** stores all command line parameters in a file and duplicates stdout you see during the experiment to another file. Additionaly, it saves exact git commit hash so you can easily checkout to it later and run the same code with the same parameters.
* Restoring a model is now really painless! Since **mag** saves all the parameters you used to run the experiment, all you need to restore a model is to provide a path to a saved experiment.


Let's consider an example:
``` python
from sklearn.datasets import load_iris
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score

from mag.experiment import Experiment

svm_config = dict(
    C=10,
    gamma=0.01
)

iris = load_iris()

with Experiment(config=svm_config) as experiment:

    model = SVC(C=experiment.config.C, gamma=experiment.config.gamma)
    score = cross_val_score(model, X=iris.data, y=iris.target, scoring="accuracy").mean()
    print("Accuracy is", score)
```
This snippet creates the following folder structure:
```
experiments
└── 10|0.01
    ├── config.json
    └── log
```

Where ```10|0.01``` is an identifier of the current experiment (which is inferred from the defined config) and log
is a log file (in the basic case, it is just a duplicate of the stdout).

Various other options are available and will be documented soon.

**Installation**

To install, clone the repository and then use ```pip install .``` or run ```pip install git+https://github.com/ex4sperans/mag.git``` to install directly from GitHub. The repository will be added to PyPI soon to simplify the installation.
