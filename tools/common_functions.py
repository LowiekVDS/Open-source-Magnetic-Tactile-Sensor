import pandas as pd
import os
import numpy as np

def prepare_data_for_fitting(name, ARRAY_SIZE=4, SENSOR_LAG = 25, faulty=True):
    
    print(f"Preparing data for fitting: {name}")
    columns = [f'X{i}' for i in range(ARRAY_SIZE)] + [f'Y{i}' for i in range(ARRAY_SIZE)] + [f'Z{i}' for i in range(ARRAY_SIZE)]
    
    # Read in the data
    TFdata = read_csv_file(f"../data/raw/TF/{name}.csv") 
    sensordata = read_csv_file(f'../data/raw/sensor/{name}.csv')
    
    # Take rolling mean
    TFdata['F_x'] = TFdata['F_x'].rolling(window=100).mean()
    TFdata['F_y'] = TFdata['F_y'].rolling(window=100).mean()
    TFdata['F_z'] = TFdata['F_z'].rolling(window=100).mean()

    # Time sync
    data = time_sync_data(sensordata, TFdata, SENSOR_LAG / 1000)
    
    # Remove rows containing NaN values
    data = data.dropna()
    
    # Offset and scale
    data = offset_data(data, columns, 100)
    
    # Remove other columns
    data = data.drop(columns=['t_robot', 'R_x', 'R_y', 'R_z'])

    return data

def unwrap_data(data, columns, threshold=1000):
    
    for col in columns:
        
        np_data = data[col].to_numpy()

        diff = np.diff(np_data)
                
        wrap_points = np.where(np.abs(diff) > threshold)[0]
                
        for point in wrap_points:
            np_data[point+1:] -= diff[point]

        data[col] = np_data

    return data

def read_csv_file(path):
    """
    Reads a CSV file from the specified path and returns the data as a pandas DataFrame.
    
    Parameters:
        path (str): The path to the CSV file.
        
    Returns:
        pandas.DataFrame: The data read from the CSV file.
    """
    
    data = pd.read_csv(os.path.join(os.getcwd(), path))
    
    nr_of_columns = len(data.columns)
    
    # Remove units
    for col in data.columns:
        data[col .split(' ')[0]] = data[col]
    
    # Remove old columns
    data = data.iloc[:, nr_of_columns:]    
    
    return data
    
def read_csv_files(paths):
    """
    Reads all CSV files from the specified path and returns the data as a pandas DataFrame.
    
    Parameters:
        paths (list): list of paths
        
    Returns:
        pandas.DataFrame: The data read from the CSV files.
    """
    
    data = pd.DataFrame()
    
    for p in paths:
        data = pd.concat([data, read_csv_file(p)], ignore_index=True)
    
    return data    

def time_sync_data(df1, df2, df1_lag):

    df1['t_wall'] -= df1_lag
    
    df1_is_first = df1['t_wall'][0] < df2['t_wall'][0]
    sensor_is_last = df1['t_wall'][len(df1)-1] > df2['t_wall'][len(df2)-1]

    if df1_is_first:
        start = df2['t_wall'][0]
    else:
        start = df1['t_wall'][0]
    
    if sensor_is_last:
        end = df1['t_wall'][len(df1)-1]
    else:
        end = df2['t_wall'][len(df2)-1]
    
    # Clip data to start at the same time and also to end at the same time
    df2 = df2[df2['t_wall'] >= start]
    df1 = df1[df1['t_wall'] >= start]
    df2 = df2[df2['t_wall'] <= end]
    df1 = df1[df1['t_wall'] <= end]

    combined = pd.concat([df1, df2], ignore_index=True, sort=False).sort_values(by=['t_wall'])

    combined.set_index('t_wall')
    combined = combined.apply(lambda x: x.interpolate(method='linear')).reset_index()
    
    return combined

def offset_data(data, columns, window=100, startup=100):

    for col in columns:
        data[col] -= np.mean(data[col][startup:startup+window])
        data[col] /= 1000
        
    return data

def normalize_center_data(data, columns):
    """
    Normalizes the data in the specified columns.
    
    Parameters:
        data (pandas.DataFrame): The data to be normalized.
        columns (list): The columns to be normalized.
        
    Returns:
        pandas.DataFrame: The normalized data.
    """
    
    for col in columns:
        data[col] = data[col] / (data[col].max() - data[col].min())
        data[col] = (data[col] - data[col].mean())
        
    return data