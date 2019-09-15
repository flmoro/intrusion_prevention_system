from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from app.core.util import timing


class Detector:
    """Detects anomalous flows using supervised machine learning models.

    Attributes
    ----------
    self.classifier: dict
        Supervised machine learning object."""

    def __init__(self, classifier):
        self.classifier = classifier

    def define_tuning(self, preprocessing, kfolds, tmp_directory):
        """Exhaustive search over specified parameters values for an machine
        learning algorithm.

        Parameters
        ----------
        preprocessing: obj
            Preprocessing object.
        kfolds: int
            Number of k folds.
        tmp_directory: str
            Absoulute path of a temporary directory to cache each transformer
            after calling fit. It avoids computing the fit transformers many
            times in a case of grid search"""

        if preprocessing:
            # chaining estimators in a fixed sequence of steps.
            self.classifier['obj'] = Pipeline(
                [('prep', preprocessing), ('clf', self.classifier['obj'])],
                memory=tmp_directory)

            # key method and list function must be kept to avoid repetitions.
            for key in list(self.classifier['param'].keys()):
                value = self.classifier['param'].pop(key)
                self.classifier['param'][f'clf__{key}'] = value

        self.classifier['obj'] = GridSearchCV(self.classifier['obj'],
                                              self.classifier['param'],
                                              cv=kfolds)

    @timing
    def train(self, training_features, training_labels):
        """Trains the machine learning algorithm.

        Parameters
        ----------
        training_features: list
            Features to training the algorithm.
        training_labels: list
            Correct features labels to training the algorithm.

        Returns
        -------
        param
            Best parameters found by grid search."""

        self.classifier['obj'].fit(training_features, training_labels)

        return self.classifier['obj'].best_params_

    @timing
    def test(self, test_features):
        """Executes the machine learning algorithm.

        Parameters
        ----------
        test_features: list
            Features to classify.

        Returns
        -------
        pred
            Prediction for each test entry."""

        return self.classifier['obj'].predict(test_features)


classifiers_obj = {
    'decision_tree': {
        'obj': DecisionTreeClassifier(),
        'param': {
            'criterion': ['gini', 'entropy'],
            'splitter': ['best', 'random'],
            'max_depth': [3, 9, 15, 21],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [2, 5, 10],
            'max_features': [None, 'sqrt']
        }
    },

    'gaussian_naive_bayes': {
        'obj': GaussianNB(),
        'param': {
            'var_smoothing': [0.00001, 0.01, 0.1, 1.0]
        }
    },

    'k-nearest_neighbors': {
        'obj': KNeighborsClassifier(),
        'param': {
            'n_neighbors': [5, 10, 15],
            'weights': ['uniform', 'distance'],
            'algorithm': ['ball_tree', 'kd_tree'],
            'leaf_size': [10, 20, 30]
        }
    },

    'multi-layer_perceptron': {
        'obj': MLPClassifier(),
        'param': {
            'hidden_layer_sizes': [(10,), (15, 10), (20, 15, 10)],
            'activation': ['identity', 'logistic', 'tanh', 'relu'],
            'solver': ['adam', 'lbfgs', 'sgd'],
            'alpha': [0.0001, 0.001, 0.01, 0.1],
            'max_iter': [50, 100, 200, 500]
        }
    },

    'support_vector_machine': {
        'obj': SVC(),
        'param': {
            'kernel': ['rbf'],
            'C': [0.1, 1.0, 10.0],
            'gamma': [0.001, 0.01, 0.1],
            'cache_size': [5000.0]
        }
    }
}
