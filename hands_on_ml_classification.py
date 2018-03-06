import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from sklearn.datasets import fetch_mldata
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_val_score
from sklearn.base import BaseEstimator, clone
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score
from sklearn.metrics import precision_recall_curve, roc_curve, roc_auc_score
from sklearn.ensemble import RandomForestClassifier


class Never5Classifier(BaseEstimator):
    def fit(self, X, y=None):
        pass
    def predict(self, X):
        return np.zeros((len(X), 1), dtype=bool)


def main():
    mnist = fetch_mldata('MNIST original')
    X_train, X_test, y_train, y_test = split_mnist_sets(mnist)
    some_digit = X_train[36000]
    X_train, y_train = shuffle_data(X_train, y_train)
    y_train_5 = (y_train == 5)
    y_test_5 = (y_test == 5)
    forest_clf = RandomForestClassifier(random_state=42)
    y_probas_forest = cross_val_predict(forest_clf, X_train, y_train_5, cv=3, method='predict_proba')
    y_scores_forest = y_probas_forest[:, 1]
    fpr_forest, tpr_forest, thresholds_forest = roc_curve(y_train_5, y_scores_forest)


def try_sgd_clf(X_train, y_train_5):
    sgd_clf = SGDClassifier()
    y_scores = cross_val_predict(sgd_clf, X_train, y_train_5, cv=3, method='decision_function')
    precisions, recalls, thresholds = precision_recall_curve(y_train_5, y_scores)
    y_train_pred_90 = (y_scores > 85000)
    print_precision_recall_f1(y_train_5, y_train_pred_90)
    fpr, tpr, thresholds = roc_curve(y_train_5, y_scores)
    roc_auc = roc_auc_score(y_train_5, y_scores)


def plot_roc_curve(tpr, fpr, label=None):
    plt.plot(fpr, tpr, linewidth=2, label=label)
    plt.plot([0, 1], [0, 1], 'k--')
    plt.axis([0, 1, 0, 1])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')



def plot_precision_vs_recall(precisions, recalls):
    plt.plot(recalls[:-1], precisions[:-1], 'g-')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.axis([0, 1, 0, 1])


def plot_precision_recall_vs_threshold(precisions, recalls, thresholds):
    plt.plot(thresholds, precisions[:-1], 'b--', label='Precision')
    plt.plot(thresholds, recalls[:-1], 'g-', label='Recall')
    plt.xlabel('Threshold')
    plt.legend(loc='upper left')
    plt.ylim([0, 1])


def print_precision_recall_f1(y_train, y_train_predict):
    print(f'Precision: {precision_score(y_train, y_train_predict):6.4f}\n'
          f'Recall: {recall_score(y_train, y_train_predict):6.4f}\n'
          f'F1: {f1_score(y_train, y_train_predict):6.4f}')


def calc_clf_metrics(clf, X_train, y_train, cv=3):
    y_train_predict = cross_val_predict(clf, X_train, y_train, cv=cv)
    print(f'Confusion matrix:\n{confusion_matrix(y_train, y_train_predict)}\n')
    print_precision_recall_f1(y_train, y_train_predict)


def custom_cross_validation(X, y, clf, n_splits=3, random_state=42):
    skfolds = StratifiedKFold(n_splits=n_splits, random_state=random_state)
    cv_score = []
    for train_index, test_index in skfolds.split(X, y):
        clone_clf = clone(clf)
        X_train_folds = X[train_index]
        y_train_folds = y[train_index]
        X_test_fold = X[test_index]
        y_test_fold = y[test_index]

        clone_clf.fit(X_train_folds, y_train_folds)
        y_pred = clone_clf.predict(X_test_fold)
        n_correct = sum(y_pred == y_test_fold)
        cv_score.append(n_correct / len(y_pred))
    return cv_score


def shuffle_data(X, y):
    if X.shape[0] != y.shape[0]:
        raise ValueError('X and y must have the same number of rows')
    shuffle_index = np.random.permutation(len(X))
    return X[shuffle_index], y[shuffle_index]


def show_digit(digit):
    digit_image = digit.reshape(28, 28)
    plt.imshow(digit_image, cmap=matplotlib.cm.binary, interpolation='nearest')
    plt.axis('off')
    plt.show()


def split_mnist_sets(mnist):
    X, y = mnist['data'], mnist['target']
    X_train, X_test, y_train, y_test = X[:60000], X[60000:], y[:60000], y[60000:]
    return X_train, X_test, y_train, y_test


if __name__ == '__main__':
    main()
