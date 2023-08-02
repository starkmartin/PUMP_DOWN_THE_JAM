import os
import pandas as pd
import numpy as np

# from https://stackoverflow.com/questions/11130156/suppress-stdout-stderr-print-from-python-functions

class suppress_stdout_stderr(object):
    '''
    A context manager for doing a "deep suppression" of stdout and stderr in
    Python for Prophet, i.e. will suppress all print, even if the print originates in a
    compiled C/Fortran sub-function.
       This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited (at least, I think that is why it lets exceptions through).

    '''
    def __init__(self):
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = (os.dup(1), os.dup(2))

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        # Close the null files
        os.close(self.null_fds[0])
        os.close(self.null_fds[1])


### Build a pipeline
from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import cross_validate
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.base import RegressorMixin
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error

## Create a custom Transformer to impute missing values using an interpolation over time

#Impute missing values
class InterpolateImputer(BaseEstimator, TransformerMixin):
    '''This imputer interpolates missings based on time'''
    def __init__(self): # no *args or **kargs
        pass
    def fit(self, X, y=None):
        return self  # nothing else to do - since no values are stored, and therefore no fitting is applied to test data
    def transform(self, X, y=None):
        X = X.copy()
        X = X.set_index(pd.DatetimeIndex(X.ds, freq='D')).drop('ds',axis=1)
        X = X.interpolate(method='time', limit_direction='both')
        X = X.round()
        return X.reset_index()


class CopyRegressor(RegressorMixin):
    '''This "regressor" simply copies the needed number of predictions
    from previous weekdays. It takes the values'''
    def __init__(self, horizon): # no *args or **kargs
        self.horizon = horizon
    def fit(self, y):
        # Calculate how many weeks back we have to go to get enough days
        # to predict the horizon.
        weeksback = (self.horizon - 1) // 7 + 1
        # If we need up until the very last day of training data,
        # we need different syntax for for the indexing, eg [-7:] NOT [-7:0] 
        if (-(7*weeksback)+self.horizon) == 0:
            self.previous_weekdays = y.y[-(7*weeksback):]
        else:
            self.previous_weekdays = y.y[-(7*weeksback):-(7*weeksback)+self.horizon]
            
    def predict(self):
        # Give back prediction
        return self.previous_weekdays
    
def cross_val_baseline(y,cutoffs,horizon):
    RMSE = []
    MAPE = []
    dates = []
    yhats = []
    y_s = []
    df_s = []

    for date_x in cutoffs:
        # Training date including the cutoff date
        y_train = y[y.ds <= date_x]

        # Test data, but only for the prediction horizon in days
        y_test = y[y.ds > date_x]
        y_test = y_test[:horizon]
        
        # APply the copy model, copying the days needed for the
        # prediction horizon
        model = CopyRegressor(horizon=horizon)
        model.fit(y=y_train)
        y_pred = model.predict()

        y_test['yhat'] = y_pred.values

        df_s.append(y_test.copy(deep=True))
        #

        # Append to lists for the dataframe
        RMSE.append(mean_squared_error(y_true=y_test.y,y_pred=y_pred, squared=False))
        MAPE.append(mean_absolute_percentage_error(y_true=y_test.y,y_pred=y_pred))
        dates.append(date_x)

    df_metrics = pd.DataFrame({'cutoff': dates, 'RMSE': RMSE, 'MAPE': MAPE})
    df = pd.concat(df_s)
    print('Mean MAPE is: ', df_metrics.MAPE.mean())
    print('Mean RMSE is: ', df_metrics.RMSE.mean())

    return df,df_metrics