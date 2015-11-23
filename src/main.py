'''
Copyright (C) 2015 Gina L. Sprint
Email: Gina Sprint <gsprint@eecs.wsu.edu>

This file is part of sensor_data_preprocessing.

sensor_data_preprocessing is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

sensor_data_preprocessing is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License
along with sensor_data_preprocessing.  If not, see <http://www.gnu.org/licenses/>.

OrientationFiltering --- main.py
Created on Apr 2, 2015

This code is specific to processing Shimmer3 sensor data for our ambulatory circuit
wearable sensor study. Functions of interest that could be used for other research
domains include:
1. apply_filter()
2. orient_shank()
2. orient_COM()

Dependencies:
pandas

@author: Gina Sprint and Vladimir Borisov
'''
import os
import pandas as pd

import utils
from src.utils import closest_timestamp

    
def orient_filter_shank(path, sensor_loc):
    '''
    Orient and filter the shank sensors.

    Keyword arguments:

    '''
    fname = os.path.join(path, sensor_loc + ".csv")
    session_path = os.path.split(path)[0]
    filtered_path = os.path.join(session_path, "Filtered_Ankle_Corrected")
    parameter_path = os.path.join(filtered_path, "Orientation_Parameters")
    section_plot_fname = os.path.join(parameter_path, sensor_loc + "_orientation.png")
    notes_fname = os.path.join(parameter_path, sensor_loc + "_notes.txt")
    horiz_df_fname = os.path.join(parameter_path, sensor_loc + "_config_orient_horizontal.csv")
    vert_df_fname = os.path.join(parameter_path, sensor_loc + "_config_orient_vertical.csv")
    oriented_filtered_df_fname = os.path.join(filtered_path, sensor_loc + "_oriented_filtered.csv")
    
    # row 0 is device name, row 1 is signal name, row 2 is Raw or Cal, row 3 is units
    df = pd.read_csv(fname, skiprows=[0, 2, 3], header=0, index_col=0)

    # for debugging to specify files instead of create from user
    #horiz_df = pd.read_csv(horiz_df_fname, skiprows=[0, 2, 3], header=0, index_col=0)
    #vert_df = pd.read_csv(vert_df_fname, skiprows=[0, 2, 3], header=0, index_col=0)
    horiz_df, vert_df = utils.get_user_defined_sections(fname, notes_fname, section_plot_fname, \
                                                  horiz_df_fname, vert_df_fname, df, sensor_loc)
    oriented_df = utils.orient_shank(horiz_df, vert_df, df, sensor_loc)
    oriented_filtered_df = utils.apply_filter(oriented_df.copy(), sensor_loc)
    
    utils.plot_oriented_filtered_data(df, oriented_df, oriented_filtered_df, sensor_loc)
    utils.write_data(fname, oriented_filtered_df_fname, oriented_filtered_df)
  
  
def orient_filter_COM(path):
    '''
    Orient and filter the COM sensor.

    Keyword arguments:

    '''
    fname = os.path.join(path, "HIP.csv")
    session_path = os.path.split(path)[0]
    filtered_path = os.path.join(session_path, "Filtered_Ankle_Corrected")
    oriented_filtered_df_fname = os.path.join(filtered_path, "HIP_oriented_filtered.csv")
    
    # row 0 is device name, row 1 is signal name, row 2 is Raw or Cal, row 3 is units
    df = pd.read_csv(fname, skiprows=[0, 2, 3], header=0, index_col=0)

    oriented_df = utils.orient_COM(df)
    oriented_filtered_df = utils.apply_filter(oriented_df.copy(), "HIP")
    
    utils.plot_oriented_filtered_data(df, oriented_df, oriented_filtered_df, "HIP")
    utils.write_data(fname, oriented_filtered_df_fname, oriented_filtered_df)
 
def orient_filter_assistive_device(path):
    '''
    Orient and filter the assistive device sensor.

    Keyword arguments:

    '''
    walker_or_cane = "WALKER"
    fname = os.path.join(path, "WALKER.csv")
    # this file exists because mounting was not always consistent
    # so each individual session has its own axes alignment file
    axes_fname = os.path.join(path, "DEV_axes.txt")
    session_path = os.path.split(path)[0]
    filtered_path = os.path.join(session_path, "Filtered_Ankle_Corrected")
    oriented_filtered_df_fname = os.path.join(filtered_path, "DEV_oriented_filtered.csv")
    
    # row 0 is device name, row 1 is signal name, row 2 is Raw or Cal, row 3 is units
    try: # try opening walker
        df = pd.read_csv(fname, skiprows=[0, 2, 3], header=0, index_col=0)
    except IOError: # try opening cane
        fname = os.path.join(path, "CANE.csv")
        try:
            df = pd.read_csv(fname, skiprows=[0, 2, 3], header=0, index_col=0)
            walker_or_cane = "CANE"
        except IOError:
            print "Walker or cane file DNE for this participant"
            return
    axes_df = pd.read_csv(axes_fname, header=0, index_col=0)
    
    print "axes_df"
    print axes_df
    
    oriented_df = utils.orient_assistive_device(df, axes_df)
    oriented_filtered_df = utils.apply_filter(oriented_df.copy(), walker_or_cane)
    
    utils.plot_oriented_filtered_data(df, oriented_df, oriented_filtered_df, walker_or_cane)
    utils.write_data(fname, oriented_filtered_df_fname, oriented_filtered_df)   
    
    
def chop_dev_data_after_others(path, sensor_loc):
    '''
    This is a hacky solution to chop the assistive device data after
    the other sensor files (HIP, LA, RA) have been chopped. Simply open
    the COM file and grab the first and the last timestamps for each trial
    Then chop DEV to the closest timestamps to the COM timestamps
    Chop the data files to trim them down and specify start timestamp for COM.

    Keyword arguments:

    '''
    session_path = os.path.split(path)[0]
    filtered_path = os.path.join(session_path, "Filtered_Ankle_Corrected")
    trials_path = os.path.join(session_path, "Trials")
    meta_files = os.listdir(trials_path)
    hip_T1_fname = hip_T2_fname = None
    prefix = prefix2 = None
    for fil in meta_files:
        if "META" in fil:
            if prefix is None:
                prefix = fil[:-9]
            else:
                prefix2 = fil[:-9]
        if "HIP" in fil:
            if fil[4]  == "1" or fil[4] == "3":
                hip_T1_fname = fil
            elif fil[4] == "2" or fil[4] == "4":
                hip_T2_fname = fil
    assert(hip_T1_fname is not None)
    assert(hip_T2_fname is not None)
    
    hip_T1_chopped_fname = os.path.join(trials_path, hip_T1_fname)
    hip_T2_chopped_fname = os.path.join(trials_path, hip_T2_fname)
    # cheating! just grab previously chopped dfs and start/end times for each file
    hip_T1_df = pd.read_csv(hip_T1_chopped_fname, skiprows=[0, 2, 3], header=0, index_col=0)
    hip_T2_df = pd.read_csv(hip_T2_chopped_fname, skiprows=[0, 2, 3], header=0, index_col=0)
    
    # the cheat instead of calling get_user_defined_trial_times()
    trial_times = [hip_T1_df.index[0], hip_T1_df.index[-1], 
                   hip_T2_df.index[0], hip_T2_df.index[-1]]
    
    loc_fname = os.path.join(filtered_path, sensor_loc + "_oriented_filtered.csv")
    # not all participants use an assistive device
    if os.path.isfile(loc_fname):
        chopped_df_fname = os.path.join(trials_path, prefix + "_" + sensor_loc + ".csv")
        chopped_df_fname2 = os.path.join(trials_path, prefix2 + "_" + sensor_loc + ".csv")
        utils.chop_dependent_data(loc_fname, chopped_df_fname, chopped_df_fname2, trial_times)
            
            
def chop_data(path, dependent_sensor_locs):
    '''
    Chop the data files to trim them down and specify start timestamp for COM.

    Keyword arguments:

    '''
    session_path = os.path.split(path)[0]
    filtered_path = os.path.join(session_path, "Filtered_Ankle_Corrected")
    trials_path = os.path.join(session_path, "Trials")
    meta_files = os.listdir(trials_path)
    prefix = prefix2 = None
    for fil in meta_files:
        if "META" in fil:
            if prefix is None:
                prefix = fil[:-9]
            else:
                prefix2 = fil[:-9]
    com_fname = os.path.join(filtered_path, "HIP_oriented_filtered.csv")
    chopped_plot_fname = os.path.join(filtered_path, "HIP_chopped.png")
    notes_fname = os.path.join(filtered_path, "chopping_notes.txt")
    chopped_df_fname = os.path.join(trials_path, prefix + "_HIP.csv")
    chopped_df_fname2 = os.path.join(trials_path, prefix2 + "_HIP.csv")
    
    trial_times = utils.get_user_defined_trial_times(com_fname, notes_fname, chopped_plot_fname, \
                                       chopped_df_fname, chopped_df_fname2)
    
    for sensor_loc in dependent_sensor_locs:
        loc_fname = os.path.join(filtered_path, sensor_loc + "_oriented_filtered.csv")
        # not all participants use an assistive device
        if os.path.isfile(loc_fname):
            chopped_df_fname = os.path.join(trials_path, prefix + "_" + sensor_loc + ".csv")
            chopped_df_fname2 = os.path.join(trials_path, prefix2 + "_" + sensor_loc + ".csv")
            utils.chop_dependent_data(loc_fname, chopped_df_fname, chopped_df_fname2, trial_times)
       
 
    
if __name__ == '__main__':
    # filename munging...
    home_dir = os.path.expanduser("~")
    path = os.path.join(home_dir, r"Google Drive\StLukes Research\Data\Participant_Data")
    path = os.path.join(path, r"016\016_S2_7-15-14\Timestamp_Aligned")
    # HIP, RA, LA, or DEV #os.path.basename(fname)[:-4]
    #orient_filter_shank(path, "LA")
    #orient_filter_shank(path, "RA")
    #orient_filter_COM(path)
    orient_filter_assistive_device(path)
    chop_dev_data_after_others(path, "DEV")
    #chop_data(path, ["LA", "RA"])#, "DEV"])
    
