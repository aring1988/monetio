# Reads a tdump file, outputs a Pandas DataFrame

import numpy as np
import re
import pandas as pd


def open_dataset(filename):
    """ Opens a tdump file, returns trajectory array

    Parameters
    ----------------
    filename : string
         Full file path for tdump file

    Returns
    -----------
    traj: Pandas DataFrame
         DataFrame with all trajectory information

    """

    tdump = open_tdump(filename)
    traj = get_traj(tdump)
    return traj


def open_tdump(filename):
    """Opens the tdump file

    Parameters
    ----------------
    filename: string
         Full file path for tdump file

    Returns
    -----------
    tdump: _io.TextIOWrapper
         tdump file opened in read mode, encoding UTF-8
         ready to be used by other functions in this code

    """

    tdump = open(filename)
    return tdump


def get_metinfo(tdump):
    """Finds the meteorological grid info from tdump file

    Parameters
    ----------------
    tdump: _io.TextIOWrapper
         tdump file opened in read mode, encoding UTF-8

    Returns
    -----------
    metinfo: list
          List of strings describing met model, date and time

    """

    # Going back to first line of file
    tdump.seek(0)
    # Dimensions of met file array in numpy array
    dim1 = tdump.readline().strip().replace(' ', '')
    dim1 = np.array(list(dim1))
    # Read met file info into array
    metinfo = []
    a = 0
    while a < int(dim1[0]):
        tmp = re.sub(r'\s+', ',', tdump.readline().strip())
        metinfo.append(tmp)
        a += 1
    return metinfo


def get_startlocs(tdump):
    """Finds the trajectory starting locations from the tdump file

    Parameters
    ----------------
    tdump: _io.TextIOWrapper
         tdump file opened in read mode, encoding UTF-8

    Returns
    -----------
    start_locs: Pandas DataFrame
          DataFrame describing trajectory starting date, time, location and altitudes
          Date and Time are a Datetime Object

    """

    # Going back to first line of file
    tdump.seek(0)
    # Gets the metinfo
    metinfo = get_metinfo(tdump)
    # Read next line - get number of starting locations
    dim2 = list(tdump.readline().strip().split(' '))
    start_locs = []
    b = 0
    while b < int(dim2[0]):
        tmp2 = re.sub(r'\s+', ',', tdump.readline().strip())
        tmp2 = tmp2.split(',')
        start_locs.append(tmp2)
        b += 1
    # Putting starting locations array into pandas DataFrame
    heads = ['year', 'month', 'day', 'hour', 'latitude', 'longitude', 'altitude']
    stlocs = pd.DataFrame(np.array(start_locs), columns=heads)
    cols = ['year', 'month', 'day', 'hour']
    # Joins cols into one column called time
    stlocs['time'] = stlocs[cols].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
    # Drops cols
    stlocs = stlocs.drop(cols, axis=1)
    # Reorders columns
    stlocs = stlocs[['time', 'latitude', 'longitude', 'altitude']]
    # Puts time into datetime object
    stlocs['time'] = pd.to_datetime(stlocs['time'], format='%y %m %d %H')
    return stlocs


def get_traj(tdump):
    """Finds the trajectory information from the tdump file

    Parameters
    ----------------
    tdump: _io.TextIOWrapper
         tdump file opened in read mode, encoding UTF-8

    Returns
    -----------
    traj: Pandas DataFrame
          DataFrame describing all trajectory variables
          Date and Time are a Datetime Object

    """
    # Going back to first line of file
    tdump.seek(0)
    # Gets the starting locations
    stlocs = get_startlocs(tdump)
    # Read the number (and names) of additional variables in traj file
    varibs = re.sub(r'\s+', ',', tdump.readline().strip())
    varibs = varibs.split(',')
    variables = varibs[1:]
    # Read the traj arrays into pandas dataframe
    heads = ['time', 'traj_num', 'met_grid', 'forecast_hour',
             'traj_age', 'latitude', 'longitude', 'altitude'] + variables
    traj = pd.read_csv(tdump, header=None, sep='\s+', parse_dates={'time': [2, 3, 4, 5, 6]})
    # Adds headers to dataframe
    traj.columns = heads
    # Makes all headers lowercase
    traj.columns = map(str.lower, traj.columns)
    # Puts time datetime object
    traj['time'] = pd.to_datetime(traj['time'], format='%y %m %d %H %M')
    return traj
