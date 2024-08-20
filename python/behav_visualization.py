#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 18 19:53:49 2024

@author: emmaodom
"""

import pandas as pd 
import seaborn as sns
import matplotlib.pyplot as plt
import os 
import glob
import re

#spark/polar/airflow
#%% def functions
def get_txt_path(directory):
    '''
    This function returns any file under directory that has RoiSet.zip in the filename

    Parameters
    ----------
    directory : str
        The path to the directory to search.

    Returns
    -------
    roi_set_zip : str or None
        The file path to the RoiSet.zip file, or None if not found.
    '''
    # Search for RoiSet.zip in the directory
    txt_files = glob.glob(os.path.join(directory, '*.txt'))
    # Check if any RoiSet.zip files were found
    if len(txt_files) == 0:
        print("No .txt files found.")
        return None
    return txt_files

def get_txt_df(filepath):
    df = pd.read_csv(filepath, sep='-', header=None)
    df = df.reset_index()
    #alt labels = df.columns[-2:]
    df.drop(labels=['index',2,3],axis=1,inplace=True)
    df.rename(columns={0: 'Timestamp', 1: 'Print'}, inplace=True)
    #extract data from print statements
    df['Sensor'] = df['Print'].str.extract(r'(lick|bar)', expand=False)
    df['Value'] = df['Print'].str.extract(r'(\d+)', expand=False).astype(float)
    df['Solenoid'] = df['Print'].str.contains('Solenoid Activated').astype(bool)
    df.drop(labels=['Print'],axis=1,inplace=True)
    #remove rows where solenoid is false and sensor is nan
    df = df[~(df['Sensor'].isna() & (df['Solenoid'] == 0))]
    #df.dropna(axis=0,inplace=True)
    return df
#%% test code
dirpath = '/Users/emmaodom/Dropbox (MIT)/Emma/Reach_Task_Master/lick_reaching_data'
filename = '806N_Lick_20240813_231545.txt'
#do direcotry walk thing to filter through them
filepath = os.path.join(dirpath,filename)
df = pd.read_csv(filepath, sep='-', header=None)
df = df.reset_index()
#alt labels = df.columns[-2:]
df.drop(labels=['index',2,3],axis=1,inplace=True)
df.rename(columns={0: 'Timestamp', 1: 'Print'}, inplace=True)
df['Sensor'] = df['Print'].str.extract(r'(lick|bar)', expand=False)
df['Value'] = df['Print'].str.extract(r'(\d+)', expand=False).astype(float)
#df['Solenoid'] = df['Print'].str.contains('Solenoid Activated').astype(bool)
df.drop(labels=['Print'],axis=1,inplace=True)
#df = df[~(df['Sensor'].isna() & (df['Solenoid'] == 0))]
#df.dropna(axis=0,inplace=True)
df = df.sort_values(by='Timestamp')
# Regular expression to extract animal_ID, stage, and timestamp
pattern = re.compile(r"(\d{3}[A-Z])_(.+?)_(\d{8}_\d{6})")
# Extracting the components from the filename
match = pattern.match(filename)
if match:
    animal_ID = match.group(1)
    stage = match.group(2)
    timestamp = match.group(3)
else:
    raise ValueError("Filename format does not match the expected pattern.")

df['Animal_ID'] = animal_ID
df['Stage'] = stage
df['File_Timestamp'] = timestamp
#%% * aggregate behavioral data for plotting!
#this isnt really the best place to aggeregate the data anyways emma
#should summarize after you have some performance criteria. 
#get list of behav files 
txt_files = get_txt_path(dirpath)
#parse to extract animal_ID, stage, and timestamp
pattern = re.compile(r"(\d{3}[A-Z])_(.+?)_(\d{8})_(\d{6})")
#initialize master df 
behav_df = pd.DataFrame()
i=0
for txt in txt_files:
    filename = os.path.basename(txt)
    #get parsed df 
    df = get_txt_df(txt)
    match = pattern.match(filename)
    if match:
        animal_ID = match.group(1)
        stage = match.group(2)
        date = match.group(3)
        start_time = match.group(4)
    else:
        raise ValueError('filename does not have correct pattern')
    #add identifiers to the df 
    df['Animal_ID'] = animal_ID
    df['Stage'] = stage
    df['Date'] = date
    df['Start'] = start_time
    basic_plot(df)
    behav_df = pd.concat([behav_df,df],sort=False)
    i+=1
    if i>3:
        break

#%%  maybe downsample before simple visualizaiton plots... 
#cant downsample lick and bar the same (temporal res of lick sensor is way more important than the bar temporal resolution)
def basic_plot(df):
    lick_df = df[df['Sensor']=='lick'].iloc[::10, :]
    bar_df = df[df['Sensor']=='bar'].iloc[::40, :]
    sns.lineplot(data=lick_df,x='Timestamp',y='Value',label='lick')
    sns.lineplot(data=bar_df,x='Timestamp',y='Value',label='bar')
    plt.xticks(ticks=plt.xticks()[0][::100], rotation=45)  # Adjust the slicing to change the number of ticks
    plt.legend()
    plt.show()
    
    
basic_plot(df) 