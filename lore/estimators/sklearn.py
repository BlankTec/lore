# -*- coding: utf-8 -*-
"""
scikit-learn Estimator
****************
This estimator allows you to use any scikit-learn estimator of your choice.
Note that the underlying estimator can always be accessed as ``Base(estimator).sklearn``
"""
from __future__ import absolute_import
import inspect
import logging
import warnings

import lore
import lore.estimators
from lore.env import require
from lore.util import timed, before_after_callbacks

require(lore.dependencies.SKLEARN)


class Base(lore.estimators.Base):
    def __init__(self, estimator, eval_metric='sklearn_default'):
        super(Base, self).__init__()
        self.sklearn = estimator
        self.eval_metric = eval_metric

    @before_after_callbacks
    @timed(logging.INFO)
    def fit(self, x, y, validation_x=None, validation_y=None, **sklearn_kwargs):
        self.sklearn.fit(x, y=y, **sklearn_kwargs)
        results = {'eval_metric': self.eval_metric,
                   'train': self.evaluate(x, y)}
        if validation_x is not None and validation_y is not None:
            results['validate'] = self.evaluate(validation_x, validation_y)
        return results

    @before_after_callbacks
    @timed(logging.INFO)
    def predict(self, dataframe):
        return self.sklearn.predict(dataframe)

    @before_after_callbacks
    @timed(logging.INFO)
    def evaluate(self, x, y):
        return self.sklearn.score(x, y)

    @before_after_callbacks
    @timed(logging.INFO)
    def score(self, x, y):
        return self.evaluate(x, y)


class SKLearn(Base):
    def __init__(self, estimator):
        frame, filename, line_number, function_name, lines, index = inspect.stack()[1]
        warnings.showwarning('Please import SKLearn with "from lore.estimators.sklearn import Base"',
                             DeprecationWarning,
                             filename, line_number)
        super(SKLearn, self).__init__(estimator)


class Regression(Base):
    pass


class BinaryClassifier(Base):
    def __init__(self, estimator):
        super(BinaryClassifier, self).__init__(estimator, eval_metric='logloss')

    @before_after_callbacks
    @timed(logging.INFO)
    def evaluate(self, x, y):
        import sklearn
        y_pred = self.predict_proba(x)
        return sklearn.metrics.log_loss(y, y_pred)

    @before_after_callbacks
    @timed(logging.INFO)
    def score(self, x, y):
        return self.evaluate(x, y)

    @before_after_callbacks
    @timed(logging.INFO)
    def predict_proba(self, dataframe):
        """Predict probabilities using the model
        :param dataframe: Dataframe against which to make predictions
        """
        return self.sklearn.predict_proba(dataframe)


class MutliClassifier(Base):
    pass
