#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 18 19:53:49 2024

@author: emmaodom
"""
import numpy as np
import pandas as pd 
import seaborn as sns
import matplotlib.pyplot as plt
import os 
import glob
import re
import shutil
from scipy.signal import butter, filtfilt
from scipy.signal import medfilt
from scipy.signal import savgol_filter
#spark/polar/airflow
#%% get data functions
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
    txt_files = glob.glob(os.path.join(directory, '**', '*.txt'), recursive=True)
    # Check if any RoiSet.zip files were found
    if len(txt_files) == 0:
        print("No .txt files found.")
        return None
    return txt_files

def get_txt_df(filepath):
    if os.path.getsize(filepath) == 0:
        print(f"Skipping {filepath}: File is empty")
        return None  # Skip empty files

    #includes substantial preprocessing to make a useable dataframe!
    df = pd.read_csv(filepath, sep='-', header=None, on_bad_lines='skip')
    df = df.reset_index()
    #alt labels = df.columns[-2:]
    df.drop(labels=['index',2,3],axis=1,inplace=True) ##flag this, causing errors in new setup help
    df.rename(columns={0: 'Timestamp', 1: 'Print'}, inplace=True)
    #extract data from print statements
    df['Print'] = df['Print'].astype(str)
    df = df[~df['Print'].str.contains('Solenoid pin state')]
    df['Sensor'] = df['Print'].str.extract(r'(lick|bar)', expand=False)
    df['Value'] = df['Print'].str.extract(r'(\d+)', expand=False).astype(float)
    df['Solenoid'] = df['Print'].str.contains('Solenoid Activated').astype(bool)
    df.drop(labels=['Print'],axis=1,inplace=True)
    #remove rows where solenoid is false and sensor is nan
    df = df[~(df['Sensor'].isna() & (df['Solenoid'] == 0))]
    #df.dropna(axis=0,inplace=True)
    df = convert_timestamps(df)
    df = lick_detection(df)
    return df

def convert_timestamps(df):
    """
    Convert the Timestamp column to datetime format, ensuring the correct interpretation of hours, minutes, seconds, and milliseconds.
    """
    df['Timestamp'] = df['Timestamp'].str.strip()
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%H:%M:%S.%f')
    return df

def lick_detection(df, sensor='lick', percentile=0.1, m=2, min_val=15):
    """ detects lick when snesor value is m stdevs above the lowext x percentile 
    thanks chatgpt:)
    Add a boolean column 'Lick_Detected' to the DataFrame, indicating whether a lick was detected.

    Parameters:
    df (pd.DataFrame): The input DataFrame with lick data.
    sensor (str): The sensor to detect licks for, default is 'lick'.
    percentile (float): The percentile to use for the baseline, default is 10th percentile.
    stdev_multiplier (float): The number of standard deviations above the baseline to set the threshold, default is 2.

    Returns:
    pd.DataFrame: The DataFrame with an added 'Lick_Detected' boolean column.
    """
    # Filter the DataFrame to include only the relevant sensor data
    sensor_df = df[df['Sensor'] == sensor]
    # Calculate the baseline using the specified percentile
    baseline_value = sensor_df['Value'].quantile(percentile)
    # Calculate the standard deviation
    stdev_value = sensor_df['Value'].std()
    # Set the lick detection threshold
    threshold = baseline_value + m * stdev_value
    # Add a boolean column indicating whether each value exceeds the threshold
    df['Lick_Detected'] = False
    df.loc[df['Sensor'] == sensor, 'Lick_Detected'] = sensor_df['Value'] > threshold
    df.loc[df['Sensor'] == sensor, 'Lick_Detected'] = sensor_df['Value'] > min_val
    return df

#%% *filtering functions
def downsample(data, factor):
    return data[::factor]

def butter_lowpass_filter(data, cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data)
    return y

def median_filter(data, kernel_size=3):
    return medfilt(data, kernel_size=kernel_size)

def get_sampling_rate(df):
    #gets me a sampling rate for each sensor! direct chatgpt, but hey it works.
    if not pd.api.types.is_datetime64_any_dtype(df['Timestamp']):
        # Step 1: Clean the 'Timestamp' column by stripping whitespace
        df['Timestamp'] = df['Timestamp'].str.strip()
        # Step 2: Convert 'Timestamp' column to datetime with error handling
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%H:%M:%S.%f', errors='coerce')
        # Check for any rows where the conversion failed (i.e., where Timestamp is NaT)
        failed_conversions = df[df['Timestamp'].isna()]
        if not failed_conversions.empty:
            print("Rows with failed Timestamp conversions:")
            print(failed_conversions)
    # Step 3: Calculate time differences for each sensor if conversion was successful
    df['Time_Diff'] = df.groupby('Sensor')['Timestamp'].diff()
    # Step 4: Calculate the sampling frequency for each sensor
    sampling_freq = df.groupby('Sensor')['Time_Diff'].apply(lambda x: 1 / x.mean().total_seconds())
    # Display the results
    #df.drop(['Time_Diff'])
    df.drop(['Time_Diff'], axis=1, inplace=True, errors='ignore')
    print(sampling_freq)
    return(sampling_freq)
#%%  *visualization functions
#maybe downsample before simple visualizaiton plots... 
#cant downsample lick and bar the same factpr (temporal res of lick sensor is way more important than the bar temporal resolution)
import matplotlib.dates as mdates
def basic_plot(df, animal_ID, date, stage, dots = True, which_dots = 'Solenoid'):
    #sort data by sensor type and lineplot 
    lick_df = df[df['Sensor']=='lick'].iloc[::10, :]
    bar_df = df[df['Sensor']=='bar'].iloc[::40, :]
    sns.lineplot(data=lick_df,x='Timestamp',y='Value',label='lick')
    sns.lineplot(data=bar_df,x='Timestamp',y='Value',label='bar')
    #dots for solenoid activations
    if dots:
        dots_df = df[df[which_dots]==True]
        scale = 1.2*bar_df['Value'].max()
        y_ = scale*np.ones_like(dots_df['Value'])
        plt.scatter(dots_df['Timestamp'],y_,color='red',s=2,label=which_dots,zorder=5)
    #set x-ticks 
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.xticks(rotation=45) 
    #label things
    plt.title(f"{stage} Animal {animal_ID} - {date}")
    plt.legend()
    plt.show()   
#example/test call
#basic_plot(df,animal_ID,date,stage='Lick', dots=True, which_dots='Lick_Detected') 

def smoothed_plot(df, animal_ID, date, stage,order=2,kernel_size=30,dots = True, which_dots = 'Solenoid'):
    #fs_lick,fs_bar,cutoff_freq=0.2 used to be inputs for low-pass filter
    # Apply downsampling
    lick_df = df[df['Sensor'] == 'lick'].iloc[::10, :]
    bar_df = df[df['Sensor'] == 'bar'].iloc[::40, :]
    
    # Apply low-pass filter to smooth the data
    #lick_df['Smoothed_Value'] = butter_lowpass_filter(lick_df['Value'], cutoff=cutoff_freq, fs=fs_lick,order=order)
    # Apply a Savitzky-Golay filter
    lick_df['Smoothed_Value'] = savgol_filter(lick_df['Value'], window_length=7, polyorder=2)
    bar_df['Smoothed_Value'] = median_filter(bar_df['Value'], kernel_size=kernel_size)
    
    # Plotting
    sns.lineplot(data=lick_df, x='Timestamp', y='Smoothed_Value', label='lick')
    sns.lineplot(data=bar_df, x='Timestamp', y='Smoothed_Value', label='bar')
    #scatter
    if dots:
        dots_df = df[df[which_dots]==True]
        scale = 1.2*bar_df['Value'].max()
        y_ = scale*np.ones_like(dots_df['Value'])
        plt.scatter(dots_df['Timestamp'],y_,color='red',s=2,label=which_dots,zorder=5)
        
    #set x-ticks 
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.xticks(rotation=45) 
    plt.title(f"{stage} Animal {animal_ID} - {date} \n bar: median_filter lick: savgol_filter")
    plt.legend()
    plt.show()
#%% * organize files into folders by animal_ID
# Define the directory containing the files
source_dir = '//Users/emmaodom/Dropbox (MIT)/Emma/Reach_Task_Master/lick_reaching_data'
# Get a list of all files in the source directory
files = os.listdir(source_dir)
# Define a pattern to match the animal ID (3 digits followed by 1 letter)
pattern = re.compile(r'^(\d{3}[A-Z])')
# Process each file
for filename in files:
    match = pattern.match(filename)
    if match:
        animal_id = match.group(1)
        # Create a new directory for this animal ID if it doesn't exist
        save_dir = os.path.join(source_dir, animal_id)
        os.makedirs(save_dir, exist_ok=True)
        # Move the file to the new directory
        shutil.move(os.path.join(source_dir, filename), os.path.join(save_dir, filename))
#%% * delete empty text files

def delete_empty_txt_files(directory):
    for dirpath, _, filenames in os.walk(directory):
        for file in filenames:
            if file.endswith(".txt"):
                filepath = os.path.join(dirpath, file)
                # Check if the file is empty
                if os.path.getsize(filepath) == 0:
                    print(f"Deleting empty file: {filepath}")
                    os.remove(filepath)

# Example usage
directory_path = '/Users/emmaodom/Dropbox (MIT)/Emma/Reach_Task_Master/lick_reaching_data'  # Replace with the path to your directory
delete_empty_txt_files(directory_path)

#%% ignore unless... in the case you would like to make subdirectories for dates
# Define the directory containing the files
source_dir = '/path/to/your/lick_reaching_data'
destination_base_dir = '/path/to/destination'  # Base directory for new directories

# Get a list of all files in the source directory
files = os.listdir(source_dir)

# Define a pattern to match the animal ID (3 digits followed by 1 letter) and date (8 digits)
pattern = re.compile(r'^(\d{3}[A-Z])_.*?_(\d{8})')

# Process each file
for filename in files:
    match = pattern.match(filename)
    if match:
        animal_id = match.group(1)
        date = match.group(2)
        
        # Create a new directory for this animal ID if it doesn't exist
        animal_dir = os.path.join(destination_base_dir, animal_id)
        os.makedirs(animal_dir, exist_ok=True)
        
        # Create a subdirectory for the date within the animal ID directory
        date_dir = os.path.join(animal_dir, date)
        os.makedirs(date_dir, exist_ok=True)
        
        # Move the file to the appropriate date subdirectory
        shutil.move(os.path.join(source_dir, filename), os.path.join(date_dir, filename))

#%% test code
dirpath = '/Users/emmaodom/Dropbox (MIT)/Emma/Reach_Task_Master/lick_reaching_data/808T'
filename = '808T_Lick_20240813_223132.txt'
#do direcotry walk thing to filter through them
filepath = os.path.join(dirpath,filename)
df = pd.read_csv(filepath, sep='-', header=None, on_bad_lines='skip')
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
#%% specific session plot
filepath = '/Users/emmaodom/Dropbox (MIT)/Emma/Reach_Task_Master/lick_reaching_data/808T/808T_LickReach_20240909_170952.txt'
filename = os.path.basename(filepath)
df = get_txt_df(filepath)
# Regular expression to extract animal_ID, stage, and timestamp
pattern = re.compile(r"(\d{3}[A-Z])_(.+?)_(\d{8}_\d{6})")
# Extracting the components from the filename
match = pattern.match(filename)
if match:
    animal_ID = match.group(1)
    stage = match.group(2)
    timestamp = match.group(3)
basic_plot(df, animal_ID = animal_ID, date=date, stage=stage, dots=True, which_dots='Lick_Detected')
smoothed_plot(df, animal_ID = animal_ID, date=date, stage=stage, kernel_size = 99, dots=True, which_dots='Lick_Detected')
#%% * plot all sessions. has capability to aggregate the raw data across all sessions
#NEED TO FIX GET_TXT_DF TO BE ABLE TO PLOT ALL SESSIONS , REINDEX WAS CUSTOMIZED AND DOESNT NOT APPLY TO NEW TXT FILES UGH
'''despite agg. capability, this is not the best place to aggeregate the data
should summarize after you have some performance criteria. 
use this script for visualization of performance criteria as you develop them'''
animal_path = '/Users/emmaodom/Dropbox (MIT)/Emma/Reach_Task_Master/lick_reaching_data/277T'
#get list of behav files 
txt_files = get_txt_path(animal_path)
#parse to extract animal_ID, stage, and timestamp
pattern = re.compile(r"(\d{3}[A-Z])_(.+?)_(\d{8})_(\d{6})")
#initialize master df 
##behav_df = pd.DataFrame()
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
    #if recording before 6 am, set the date back one day

    # Convert start_time to a datetime object to check the hour
    start_time = pd.to_datetime(start_time, format='%H%M%S')
    # Adjust Date if Start time is before 6 AM
    if start_time.hour < 6:
        df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d') - pd.Timedelta(days=1)
    else:
        df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
    
    basic_plot(df, animal_ID = animal_ID, date=date, stage=stage, dots=True, which_dots='Lick_Detected')
    fs = get_sampling_rate(df) #prev used as inputs to lowpass filter
    smoothed_plot(df, animal_ID = animal_ID, date=date, stage=stage, kernel_size = 99, dots=True, which_dots='Lick_Detected')
    ##behav_df = pd.concat([behav_df,df],sort=False)
    i+=1
   #if i>3:
        #break  
    
#%%* SUMMARIZE BEHAVIOR
#interim pausing on how to get a sort of num correct and num failed trails. (requires weird timing things)
#probably do need to address the error from reindexing when reading into a dataframe.. 
data_path = '/Users/emmaodom/Dropbox (MIT)/Emma/Reach_Task_Master/lick_reaching_data'
#get list of behav files 
txt_files = get_txt_path(data_path)
#parse to extract animal_ID, stage, and timestamp
pattern = re.compile(r"(\d{3}[A-Z])_(.+?)_(\d{8})_(\d{6})")
#initialize behav df 
behav_df = pd.DataFrame()
i=0
for txt in txt_files:
    filename = os.path.basename(txt)
    try:
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
        #get performance metrics
        bar_holds = df['Solenoid'].sum() #num of solenoid activations represents how many times bar was correctly held for 1.5 sec
        num_licks = df['Lick_Detected'].sum()
        dur = df['Timestamp'].max() - df['Timestamp'].min()
        # If recording before 6 am, set the date back one day
        # Convert start_time to a datetime object to check the hour
        start_time = pd.to_datetime(start_time, format='%H%M%S')
        # Adjust Date if Start time is before 6 AM
        if start_time.hour < 6:
            date = pd.to_datetime(date, format='%Y%m%d') - pd.Timedelta(days=1)
        else:
            date = pd.to_datetime(date, format='%Y%m%d')
        date = date.strftime('%Y-%m-%d')
        start_time = start_time.strftime('%H:%M:%S')
        #append data (identiying info + behav metrics)
        df_ = pd.DataFrame({
            'filename':[filename],
            'animal_ID':[animal_ID],
            'stage':[stage],
            'date':[date],
            'start':[start_time],
            'bar_holds':[bar_holds],
            'num_licks':[num_licks],
            'duration(min)':[dur.total_seconds()/60]
            })
        behav_df = pd.concat([behav_df,df_],sort=False,ignore_index=True)
        #basic visualization per session
        #basic_plot(df, animal_ID = animal_ID, date=date, stage=stage, dots=True, which_dots='Lick_Detected')
    except Exception as e:
        print(f"Error processing file: '{filename}' Error: {e}")
        continue
    i+=1
    #if i>3:
     #   break  
#%%
#save to csv 
save_path = '/Users/emmaodom/Dropbox (MIT)/Emma/Reach_Task_Master/data_summary'
output_csv_path = os.path.join(save_path, "raw_behavior_summary.csv")
behav_df.to_csv(output_csv_path, index=False)
print(f"Saved measurements to {output_csv_path}")
#%% test lick threshold
lick_df = df[df['Sensor']=='lick']
# Calculate the baseline as a low percentile (e.g., 10th percentile)
baseline_value = lick_df['Value'].quantile(0.1)

# Calculate the standard deviation
stdev_value = lick_df['Value'].std()

# Set the threshold for detecting licks
threshold = baseline_value + 2 * stdev_value

# Detect licks above the threshold
num_licks = (lick_df['Value'] > threshold).sum()

print(f"Baseline Value (10th Percentile): {baseline_value}")
print(f"Standard Deviation: {stdev_value}")
print(f"Lick Detection Threshold: {threshold}")
print(f"Number of Licks Detected: {num_licks}")

#%% to get some summary values?
# Group by 'AnimalID' and 'Region', then calculate unique slices per group
summary = behav_df.groupby(['AnimalID', 'Origin', 'Region'])['Slice'].nunique().reset_index()

# Rename the column for clarity
unique_slices.rename(columns={'Slice': 'UniqueSlices'}, inplace=True)

# Display the result
print(unique_slices)

mean_unique_slices = unique_slices.groupby(['Origin', 'Region'])['UniqueSlices'].mean().reset_index()
print(mean_unique_slices)

std_unique_slices = unique_slices.groupby(['Origin', 'Region'])['UniqueSlices'].std().reset_index()
print(std_unique_slices)
#%% get trial based data, depricate when you graduate from the txt file acquisition (eyeroll)

def trial_lick(row,df):
    '''extract each set between trial_start and trial_end to see if lick_detected, try not to use for loop operation 
    record binary value if lick detected
        '''
    mask = (df['Timestamp'] >= row['trial_start']) & (df['Timestamp']<= row['trial_end'])
    return int(df.loc[mask,'Lick_Detected'].any())

min_bar_hold = 1.5 #sec
max_trial_dur = 10 #sec
filepath = '/Users/emmaodom/Dropbox (MIT)/Emma/Reach_Task_Master/lick_reaching_data/808T/808T_LickReach_20240909_170952.txt'
df = get_txt_df(filepath)
trial_start = df[df['Solenoid']==True]['Timestamp'].reset_index(drop=True)
trial_dur = trial_start.diff().shift(-1) #diff between previous and next timestamp
trial_dur = trial_dur.dt.total_seconds().fillna(min_bar_hold) 
#trial_end as next solenoid activation time OR 10 seconds after start of current trial (within row). choose lowest value 
    #trial_end = min(trial_start+trial_dur,10)
trial_end_est = trial_start + pd.to_timedelta(trial_dur, unit='s')
trial_end_10sec = trial_start + pd.to_timedelta(max_trial_dur, unit='s')

# For each trial, take the minimum of trial_end or trial_start + 10 seconds
trial_end = pd.DataFrame({'trial_end': trial_end_est, 'trial_end_10sec': trial_end_10sec}).min(axis=1)
#create trial_df 
trial_df = pd.DataFrame({
    'trial_start': trial_start,
    'trial_end': trial_end
    })
#apply trial_lick function to get lick detection per trial (passes each row of trial_df to trial_lick_detect)
trial_df['Lick_Detected'] = trial_df.apply(trial_lick, axis=1,df=df)
#report trial start time, trial duration, if lick detected in trial in a new compressed df 
print(trial_df)
#%% functions to get by trial, and session performance
def trial_lick_detect(row,df):
    '''
    row : row of pandas df
        has trial start and trial end time
    df: this should be the df extracted from txt file with all sensor data. 
    filters parent df to individual trials using start and end times
    records if any lick was detected during that trial period
    '''
    mask = (df['Timestamp'] >= row['trial_start']) & (df['Timestamp']<= row['trial_end'])
    return int(df.loc[mask,'Lick_Detected'].any())
    
def trial_performance(filepath, min_bar_hold = 1.5, max_trial_dur = 10):
    #do trial processing in here ! lah lah lah
    df = get_txt_df(filepath)
    trial_start = df[df['Solenoid']==True]['Timestamp'].reset_index(drop=True)
    trial_dur = trial_start.diff().shift(-1) #diff between previous and next timestamp
    trial_dur = trial_dur.dt.total_seconds().fillna(min_bar_hold) 
    #determine trial end time esitmate and max
    trial_end_est = trial_start + pd.to_timedelta(trial_dur, unit='s')
    trial_end_10sec = trial_start + pd.to_timedelta(max_trial_dur, unit='s')
    # For each trial, take the minimum of trial_end or trial_start + 10 seconds
    trial_end = pd.DataFrame({'trial_end': trial_end_est, 'trial_end_10sec': trial_end_10sec}).min(axis=1)
    #create trial_df 
    trial_df = pd.DataFrame({
        'trial_start': trial_start,
        'trial_end': trial_end
        })
    #apply trial_lick function to get lick detection per trial (passes each row of trial_df to trial_lick_detect)
    trial_df['Lick_Detected'] = trial_df.apply(trial_lick_detect, axis=1,df=df)
    #report trial start time, trial duration, if lick detected in trial in a new compressed df 
    return trial_df

#test trial_performance function 
'''min_bar_hold = 1.5 #sec
max_trial_dur = 10 #sec
filepath = '/Users/emmaodom/Dropbox (MIT)/Emma/Reach_Task_Master/lick_reaching_data/808T/808T_LickReach_20240909_170952.txt'
trial_perf = trial_performance(filepath, min_bar_hold, max_trial_dur)'''

def sess_performance(filepath, min_bar_hold=1.5, max_trial_dur=10):
    trial_df = trial_performance(filepath, min_bar_hold, max_trial_dur)
    total_trials = len(trial_df)
    lick_trials = trial_df['Lick_Detected'].sum()
    session_start = trial_df['trial_start'].min()
    session_end = trial_df['trial_end'].max()
    session_duration = (session_end - session_start).total_seconds() / 60  # duration in minutes
    
    filename = os.path.basename(filepath)
    match = re.match(r"(\d{3}[A-Z])_(.+?)_(\d{8})_(\d{6})", filename)
    if match:
        animal_ID, stage, date, start_time = match.groups()
    else:
        raise ValueError(f"Filename '{filename}' does not match pattern")
    
    start_time = pd.to_datetime(start_time, format='%H%M%S')
    if start_time.hour < 6:
        date = pd.to_datetime(date, format='%Y%m%d') - pd.Timedelta(days=1)
    else:
        date = pd.to_datetime(date, format='%Y%m%d')
    
    return pd.DataFrame({
        'filename': [filename],
        'animal_ID': [animal_ID],
        'stage': [stage],
        'date': [date.strftime('%Y-%m-%d')],
        'start': [start_time.strftime('%H:%M:%S')],
        'total_trials': [total_trials],
        'lick_trials': [lick_trials],
        'session_duration_min': [session_duration]
    })
#%% test new summary
# Main script
data_path = '/Users/emmaodom/Dropbox (MIT)/Emma/Reach_Task_Master/lick_reaching_data'
txt_files = get_txt_path(data_path)  # This should return a list of file paths
pattern = re.compile(r"(\d{3}[A-Z])_(.+?)_(\d{8})_(\d{6})")

behav_summary = pd.DataFrame()

for txt in txt_files:
    try:
        # Use the session performance function to get summarized metrics for each session
        sess_summary = sess_performance(txt)
        # Append the summary to the main DataFrame
        behav_summary = pd.concat([behav_summary, sess_summary], ignore_index=True, sort=False)
    except Exception as e:
        print(f"Error processing file: '{txt}' Error: {e}")
        continue

#%%
#save to csv 
save_path = '/Users/emmaodom/Dropbox (MIT)/Emma/Reach_Task_Master/data_summary'
output_csv_path = os.path.join(save_path, "behavior_summary.csv")
behav_df.to_csv(output_csv_path, index=False)
print(f"Saved measurements to {output_csv_path}")
#%%
now we need to batchify the above to all txt files, and also probably just make that into a function to simplify the looping
then record the second order compression of trial performance into a summary df. do i want to save the first order compression? i dont think so but idk. 
#%% DEPRICATED was from chatgpt
def analyze_trials(df):
    # Ensure Timestamp is in datetime format
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    # Create a list to store trial information
    trials = []
    
    # Filter solenoid activation events
    solenoid_df = df[df['Solenoid'] == True]
    
    for i, solenoid_row in solenoid_df.iterrows():
        # Trial starts at solenoid activation
        trial_start = solenoid_row['Timestamp']
        
        # Find the next solenoid activation or the end of the dataframe
        if i + 1 < len(solenoid_df):
            next_solenoid = solenoid_df.iloc[i + 1]['Timestamp']
        else:
            next_solenoid = df['Timestamp'].max()  # End of the dataframe
            
        # Trial ends either after 10 seconds or at the next solenoid activation, whichever comes first
        trial_end = min(trial_start + pd.Timedelta(seconds=10), next_solenoid)
        
        # Filter data for the current trial
        trial_data = df[(df['Timestamp'] >= trial_start) & (df['Timestamp'] < trial_end)]
        
        # Check if a lick was detected within the trial
        lick_detected = trial_data['Lick_Detected'].any()
        
        # Append trial information to the list
        trials.append({
            'Trial_Start': trial_start,
            'Trial_End': trial_end,
            'Lick_Detected': lick_detected
        })
    
    # Convert the trial information into a DataFrame for analysis
    trial_df = pd.DataFrame(trials)
    
    # Calculate total number of trials and trials where a lick was detected
    total_trials = len(trial_df)
    trials_with_lick = trial_df['Lick_Detected'].sum()

    return total_trials, trials_with_lick, trial_df
