import numpy as np
import os
import dill
from sklearn.linear_model import LinearRegression, Ridge, ARDRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer, make_column_transformer
from sklearn.pipeline import make_pipeline, make_union
from sklearn.preprocessing import PolynomialFeatures
from sklearn import set_config
from sklearn.multioutput import MultiOutputRegressor, RegressorChain
from sklearn.compose import TransformedTargetRegressor

def save_taxel_models(taxel_models, subdir, name):
    
    while '/' in name:
        subdir = os.path.join(subdir, name.split('/')[0])
        name = name.split('/')[-1]
        
    save_path = os.path.join(os.getcwd(), '..', 'models', subdir)

    if not os.path.exists(save_path):
        os.makedirs(save_path)
        
    with open(os.path.join(save_path, name), 'wb') as f:
        dill.dump(taxel_models, f)

def create_regression_pipeline_and_fit(X, Y, debug = True, preserve_time=False, alpha=1, degree=3):
  
  if preserve_time:
    split = int(len(X) * 0.99)
    X_train = X[:split]
    X_test = X[split:]
    y_train = Y[:split]
    y_test = Y[split:]
  else:
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, shuffle=True)

  pipeline = make_pipeline(
    PolynomialFeatures(degree=degree, include_bias=True), 
    LinearRegression()
  )
  
  pipeline.fit(X_train, y_train)

  if debug:
    
    print("Score: ", pipeline.score(X_test, y_test))
    print("MSE: ", mean_squared_error(y_test, pipeline.predict(X_test)))
  
  return pipeline