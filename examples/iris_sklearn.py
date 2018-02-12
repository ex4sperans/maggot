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
    score = cross_val_score(
        model, X=iris.data, y=iris.target, scoring="accuracy"
    ).mean()
    print("Accuracy is", score)
