**mag** is a lightweight and minimalistic python library that helps to keep track of numerical experiments.

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

Where ```10|0.01``` is an identifier of the current experiment (which is inferred from the defined config) as log
is a log file (in the basic case, it is just a duplicate of the stdout).

Various other options are available and will be documented soon.

**Installation**

To install, clone the repository and then use ```pip install .``` or run ```pip install git+https://github.com/ex4sperans/mag.git``` to install directly from GitHub. The repository will be added to PyPI soon to simplify the installation.
