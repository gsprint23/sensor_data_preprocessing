'''
Copyright (C) 2015 Gina L. Sprint
Email: Gina Sprint <gsprint@eecs.wsu.edu>

This file is part of MultiSensorTimestampAlignment.

MultiSensorTimestampAlignment is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

MultiSensorTimestampAlignment is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License
along with MultiSensorTimestampAlignment.  If not, see <http://www.gnu.org/licenses/>.

OrientationFiltering --- main.py
Created on Apr 2, 2015

Dependencies:
pandas

@author: Gina Sprint (with help from Vladimir Borisov)
'''
import os

import pandas as pd

import utils

def orient_shank(path, sensor_loc):
    '''
    Orient the shank sensors.

    Keyword arguments:

    '''
    fname = os.path.join(path, sensor_loc + ".csv")
    parent_dir = os.path.split(path)[0]
    parameter_path = os.path.join(parent_dir, r"Filtered_Ankle_Corrected\Orientation_Parameters")
    section_plot_fname = os.path.join(parameter_path, sensor_loc + "_orientation.png")
    notes_fname = os.path.join(parameter_path, sensor_loc + "_notes.txt")
    horiz_df_fname = os.path.join(parameter_path, sensor_loc + "_config_orient_horizontal.csv")
    vert_df_fname = os.path.join(parameter_path, sensor_loc + "_config_orient_vertical.csv")
    
    # row 0 is device name, row 1 is signal name, row 2 is Raw or Cal, row 3 is units
    df = pd.read_csv(fname, skiprows=[0, 2, 3], header=0, index_col=0)

    response = 'n'
    while response != ('y' or 'yes' or 'Y'):
        utils.plot_acceleration_data(df, sensor_loc)
        section_times = utils.choose_subsection(df.index.tolist())
        
        utils.plot_acceleration_data(df, sensor_loc, section_plot_fname, section_times)
        response = raw_input("Are these sections correct?: Y/N\n")    
        
    horiz_df = df[section_times[0]:section_times[1]]
    vert_df = df[section_times[2]:section_times[3]]
    
    utils.write_notes(notes_fname, section_times)
    utils.write_data(fname, horiz_df_fname, horiz_df)
    utils.write_data(fname, vert_df_fname, vert_df)
    
if __name__ == '__main__':
    # filename munging...
    path = r"C:\Users\Gina\Google Drive\StLukes Research\Data\Participant_Data\031\031_S1_02-17-15\Timestamp_Aligned"
    
    # HIP, RA, LA, or DEV #os.path.basename(fname)[:-4]
    orient_shank(path, "LA")
    orient_shank(path, "RA")
    
