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

OrientationFiltering --- utils.py
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
import numpy as np
import pandas as pd
import scipy.signal as signal
import matplotlib.pyplot as plt

TS_OFFSET = 500

accel_labels = ["Wide Range Accelerometer X", \
                "Wide Range Accelerometer Y", \
                "Wide Range Accelerometer Z"]

gyro_labels = ["Gyroscope X", \
               "Gyroscope Y", \
               "Gyroscope Z"]
    
def closest_timestamp(ind_list, ts):
    '''
    Find the nearest value in an index given an estimated timestamp.

    Keyword arguments:

    '''
    closest = ind_list[0]
    for val in ind_list:
        delta = abs(val-ts)

        if delta < abs(closest - ts):
            closest = val
            
    return closest

def compute_vector_norm(vec): 
    '''
    Compute vector norm.

    Keyword arguments:

    '''
    return np.linalg.norm(vec)   

def compute_avg_accel_norm(XYZ_df): 
    '''
    Compute vector norm.

    Keyword arguments:

    '''
    norms = []
    
    for i in range(len(XYZ_df)):
        norms.append(compute_vector_norm(np.array(XYZ_df.iloc[i][accel_labels])))
    
    return np.mean(norms)

def apply_filter(df, sensor_loc):
    '''
    Applied filters according to the following:
    SHIMMER DEFAULT == 51.2Hz
    [0-1] 0-nyquist= (sampling rate)/2
    NYQUIST == 25.6Hz
    0.1171875->3hz  0.00390625->.1Hz
    10 Hz Add reference... => .390625
        
    Keyword arguments:
        
    '''
    if sensor_loc == "HIP":         
        B,A = signal.butter(4, 0.00388, 'highpass') # 0.1 Hz
        D,C = signal.butter(4, 0.1171875, 'lowpass') # 3 HZ
    elif sensor_loc == "LA" or sensor_loc == "RA" or sensor_loc == "DEV":
        B,A = signal.butter(4, 0.00388, 'highpass')  # 0.1 Hz
        D,C = signal.butter(4, 0.390625, 'lowpass')  # 10 Hz
        
    # Gyro filter lowpass cutoff at 4Hz (Tong and Granat 1999)
    E, F = signal.butter(4, 0.15625, 'lowpass') # 4Hz => .15625
    
    for label in accel_labels:
        ser = df[label]
        high = signal.filtfilt(B, A, ser)
        band = signal.filtfilt(D, C, high)
        df[label] = band
        
    for label in gyro_labels:
        ser = df[label]
        low = signal.filtfilt(E, F, ser)
        df[label] = low
 
    return df

def orient_shank(horiz_df, vert_df, df, sensor_loc):
    '''
    Orient the shank sensors.

    Keyword arguments:

    '''
    print "**Orienting sensor location: " + sensor_loc + "**\n"
    horiz_avg_norm = compute_avg_accel_norm(horiz_df)
    print "Average horizontal norm: %.2lf" %(horiz_avg_norm)
    vert_avg_norm = compute_avg_accel_norm(vert_df)
    print "Average vertical norm: %.2lf\n" %(vert_avg_norm)

    # Orientation from local to body coordinate system
    # Chen (thesis) 2011 2.3.3 Mounting Calibration in 
    # Gait feature extraction from inertial body sensor networks for medical applications
    x_horiz = np.mean(horiz_df["Wide Range Accelerometer X"] * -1)
    y_horiz = np.mean(horiz_df["Wide Range Accelerometer Y"])
    z_horiz = np.mean(horiz_df["Wide Range Accelerometer Z"])

    g_prime = np.array([x_horiz, y_horiz, z_horiz]) / horiz_avg_norm

    x_vert = np.mean(vert_df["Wide Range Accelerometer X"])
    y_vert = np.mean(vert_df["Wide Range Accelerometer Y"])
    z_vert = np.mean(vert_df["Wide Range Accelerometer Z"])

    Y_B = np.array([x_vert,y_vert,z_vert]) / vert_avg_norm
    Z_B = np.cross(Y_B, g_prime)
    X_B = np.cross(Y_B, Z_B)
    
    print "G' vector: ",
    print g_prime
    print "X body vector: ",
    print X_B
    print "Y body vector: ",
    print Y_B
    print "Z body vector: ",
    print Z_B

    rotation_mat = np.array([X_B, Y_B, Z_B]).transpose()

    print "\nRotation matrix:"
    print rotation_mat
    print "\n"
    
    accel = np.array([df["Wide Range Accelerometer X"], \
                      df["Wide Range Accelerometer Y"], \
                      df["Wide Range Accelerometer Z"]])
    gyro  = np.array([df["Gyroscope X"], \
                      df["Gyroscope Y"], \
                      df["Gyroscope Z"]])
    oriented_accel = np.dot(rotation_mat, accel).transpose()
    oriented_gyro = np.dot(rotation_mat, gyro).transpose()
   
    oriented_df = df.copy()
    oriented_df["Gyroscope X"] = oriented_gyro[:, 0]
    oriented_df["Gyroscope Y"] = oriented_gyro[:, 1]
    oriented_df["Gyroscope Z"] = oriented_gyro[:, 2]
    
    oriented_df["Wide Range Accelerometer X"] = oriented_accel[:, 0]
    oriented_df["Wide Range Accelerometer Y"] = oriented_accel[:, 1]
    oriented_df["Wide Range Accelerometer Z"] = oriented_accel[:, 2]
    
    return oriented_df

def orient_COM(df):
    '''
    Orient the COM sensor.

    Keyword arguments:

    '''
    print "**Orienting sensor location: COM**\n"

    # GS: swapping X and Z to align with the international society of biomechanics
    # where X is in the direction of travel (mounted backwards on COM, *-1)
    # Y is vertical
    oriented_df = df.copy()
    oriented_df["Gyroscope X"] = df["Gyroscope Z"] * -1
    oriented_df["Gyroscope Y"] = df["Gyroscope Y"]
    oriented_df["Gyroscope Z"] = df["Gyroscope X"]
    
    oriented_df["Wide Range Accelerometer X"] = df["Wide Range Accelerometer Z"] * -1
    oriented_df["Wide Range Accelerometer Y"] = df["Wide Range Accelerometer Y"]
    oriented_df["Wide Range Accelerometer Z"] = df["Wide Range Accelerometer X"]
    
    return oriented_df

def orient_assistive_device(df, axes_df):
    '''
    Orient the assistive device sensor.

    Keyword arguments:

    '''
    print "**Orienting sensor location: DEV**\n"

    # GS: swapping X and Z to align with the international society of biomechanics
    # where X is in the direction of travel
    # Y is vertical
    oriented_df = df.copy()
    oriented_df["Gyroscope X"] = df["Gyroscope " + axes_df.ix["X"]["orig"]] * axes_df.ix["X"]["modifier"]
    oriented_df["Gyroscope Y"] = df["Gyroscope " + axes_df.ix["Y"]["orig"]] * axes_df.ix["Y"]["modifier"]
    oriented_df["Gyroscope Z"] = df["Gyroscope " + axes_df.ix["Z"]["orig"]] * axes_df.ix["Y"]["modifier"]
    
    oriented_df["Wide Range Accelerometer X"] = \
        df["Wide Range Accelerometer " + axes_df.ix["X"]["orig"]] * axes_df.ix["X"]["modifier"]
    oriented_df["Wide Range Accelerometer Y"] = \
        df["Wide Range Accelerometer " + axes_df.ix["Y"]["orig"]] * axes_df.ix["Y"]["modifier"]
    oriented_df["Wide Range Accelerometer Z"] = \
        df["Wide Range Accelerometer " + axes_df.ix["Z"]["orig"]] * axes_df.ix["Z"]["modifier"]
    
    return oriented_df

def choose_subsection(ind_list):
    '''
    Get user input specifying the start and stop times.

    Keyword arguments:

    '''
    horiz_start = float(raw_input("Enter the leg horizontal start time: "))
    horiz_end = float(raw_input("Enter the leg horizontal end time: "))
    horiz_start = closest_timestamp(ind_list, horiz_start)
    horiz_end = closest_timestamp(ind_list, horiz_end)
    print "Leg horizontal start: %lf" %(horiz_start)
    print "Leg horizontal end: %lf" %(horiz_end)
    
    vert_start = float(raw_input("Enter the leg vertical start time: "))
    vert_end = float(raw_input("Enter the leg vertical end time: "))
    vert_start = closest_timestamp(ind_list, vert_start)
    vert_end = closest_timestamp(ind_list, vert_end)
    print "Leg vertical start: %lf" %(vert_start)
    print "Leg  end: %lf" %(vert_end)
    
    return (horiz_start, horiz_end, vert_start, vert_end)

def get_user_defined_sections(fname, notes_fname, section_plot_fname, \
                              horiz_df_fname, vert_df_fname, df, sensor_loc):
    '''
    Orient and filter the shank sensors.

    Keyword arguments:

    '''
    labels = ["Horiz", "Vert"]
    response = 'n'
    while response != ('y' or 'yes' or 'Y'):
        plot_acceleration_data(df, sensor_loc)
        section_times = choose_subsection(df.index.tolist())
        
        plot_acceleration_data(df, sensor_loc, section_plot_fname, section_times, labels)
        response = raw_input("Are these sections correct?: Y/N\n")    
        
    horiz_df = df[section_times[0]:section_times[1]]
    vert_df = df[section_times[2]:section_times[3]]
    
    write_notes(notes_fname, section_times, labels)
    write_data(fname, horiz_df_fname, horiz_df)
    write_data(fname, vert_df_fname, vert_df)
    
    return horiz_df, vert_df

def choose_trial_subsection(ind_list):
    '''
    Get user input specifying the start and stop times.

    Keyword arguments:

    '''
    start = float(raw_input("Enter the first trial start time: "))
    end = float(raw_input("Enter the first trial end time: "))
    # COM start time is taking to be the literally start time i.e. time 0
    start = closest_timestamp(ind_list, start)
    # add an offset to the end to accomodate META file times
    end = closest_timestamp(ind_list, end + TS_OFFSET)
    print "First trial start: %lf" %(start)
    print "First trial end: %lf" %(end)
    
    start2 = float(raw_input("Enter the second trial start time: "))
    end2 = float(raw_input("Enter the second trial end time: "))
    start2 = closest_timestamp(ind_list, start2)
    end2 = closest_timestamp(ind_list, end2 + TS_OFFSET)
    print "Second trial start: %lf" %(start2)
    print "Second trial end: %lf" %(end2)
    
    return (start, end, start2, end2)


def get_user_defined_trial_times(fname, notes_fname, chopped_plot_fname, \
                                 chopped_df_fname, chopped_df_fname2):
    '''
    Chop the files into the trials.

    Keyword arguments:

    '''
    labels = ["T1", "T2"]
    df = pd.read_csv(fname, skiprows=[0, 2, 3], header=0, index_col=0)
    response = 'n'
    while response != ('y' or 'yes' or 'Y'):
        plot_acceleration_data(df, "HIP")
        section_times = choose_trial_subsection(df.index.tolist())
        
        plot_acceleration_data(df, "HIP", chopped_plot_fname, section_times, labels)
        response = raw_input("Are these sections correct?: Y/N\n")    
        
    chopped_df = df[section_times[0]:section_times[1]]
    chopped_df2 = df[section_times[2]:section_times[3]]
    
    write_notes(notes_fname, section_times, labels)
    write_data(fname, chopped_df_fname, chopped_df)
    write_data(fname, chopped_df_fname2, chopped_df2)
    
    return section_times

def chop_dependent_data(loc_fname, chopped_df_fname, chopped_df_fname2, trial_times):
    '''
    Chop the LA, RA, DEV, etc data files to trim them down based on start/end timestamps for COM.

    Keyword arguments:

    '''
    df = pd.read_csv(loc_fname, skiprows=[0, 2, 3], header=0, index_col=0)
    ind_list = df.index
    
    # add an offset before COM start in order to account for nearest timestamps coming before start
    start = closest_timestamp(ind_list, trial_times[0] - TS_OFFSET)
    end = closest_timestamp(ind_list, trial_times[1])
    start2 = closest_timestamp(ind_list, trial_times[2] - TS_OFFSET)
    end2 = closest_timestamp(ind_list, trial_times[3])
    
    first_trial_df = df[start:end]
    second_trial_df = df[start2:end2]
    
    write_data(loc_fname, chopped_df_fname, first_trial_df)
    write_data(loc_fname, chopped_df_fname2, second_trial_df)
    
def plot_acceleration_data(df, sensor_loc, fname=None, section_times=None, labels=None):
    '''
    Plot the acceleration so the user can find the horiz and vert sections.

    Keyword arguments:

    '''
    plt.figure()  
    plt.plot(df.index, df['Wide Range Accelerometer X'], label = 'X-axis') 
    plt.plot(df.index, df['Wide Range Accelerometer Y'], label = 'Y-axis') 
    plt.plot(df.index, df['Wide Range Accelerometer Z'], label = 'Z-axis')   
    
    if section_times is not None and labels is not None:
        plt.axvspan(section_times[0], section_times[1], facecolor='b', alpha=0.5) 
        plt.text(section_times[0], -11, labels[0], style='italic', bbox={'facecolor':'b', 'alpha':0.8, 'pad':10})
            
        plt.axvspan(section_times[2], section_times[3], facecolor='g', alpha=0.5)
        plt.text(section_times[2], -11, labels[1], style='italic', bbox={'facecolor':'g', 'alpha':0.8, 'pad':10}) 
  
   
    plt.xlabel('Timestamp')
    plt.ylabel('Acceleration [m/s^2]')
    plt.title('Sensor location: %s' %(sensor_loc))
    plt.legend()
    if fname is not None:
        plt.savefig(fname)
    plt.show()   
    
def plot_oriented_filtered_data(df, oriented_df, oriented_filtered_df, sensor_loc):
    '''
    Plot the final oriented and filtered data.

    Keyword arguments:

    '''
    plt.figure()   
    plt.subplot(311)
    plt.plot(df.index, df["Wide Range Accelerometer X"], label='X original') 
    plt.plot(df.index, oriented_df["Wide Range Accelerometer X"], label='X rotated') 
    plt.plot(df.index, oriented_filtered_df["Wide Range Accelerometer X"], label='X filtered') 
    plt.legend()
    
    plt.subplot(312)
    plt.plot(df.index, df["Wide Range Accelerometer Y"], label='Y original') 
    plt.plot(df.index, oriented_df["Wide Range Accelerometer Y"], label='Y rotated') 
    plt.plot(df.index, oriented_filtered_df["Wide Range Accelerometer Y"], label='Y filtered') 
    plt.legend()
    
    plt.subplot(313) 
    plt.plot(df.index, df["Wide Range Accelerometer Z"], label='Z original') 
    plt.plot(df.index, oriented_df["Wide Range Accelerometer Z"], label='Z rotated') 
    plt.plot(df.index, oriented_filtered_df["Wide Range Accelerometer Z"], label='Z filtered') 
    plt.xlabel('Timestamp')
    plt.ylabel('Acceleration [m/s^2]')
    plt.legend()
    
    plt.figure()
    plt.subplot(311)
    plt.plot(df.index, df["Gyroscope X"], label='X original') 
    plt.plot(df.index, oriented_df["Gyroscope X"], label='X rotated') 
    plt.plot(df.index, oriented_filtered_df["Gyroscope X"], label='X filtered') 
    plt.legend()
        
    plt.subplot(312)
    plt.plot(df.index, df["Gyroscope Y"], label='Y original') 
    plt.plot(df.index, oriented_df["Gyroscope Y"], label='Y rotated') 
    plt.plot(df.index, oriented_filtered_df["Gyroscope Y"], label='Y filtered') 
    plt.legend()
    
    plt.subplot(313)
    plt.plot(df.index, df["Gyroscope Z"], label='Z original') 
    plt.plot(df.index, oriented_df["Gyroscope Z"], label='Z rotated') 
    plt.plot(df.index, oriented_filtered_df["Gyroscope Z"], label='Z filtered') 
    plt.xlabel('Timestamp')
    plt.ylabel('Angular velocity [deg/s]')
    plt.legend()
    
    plt.show()
    
def write_notes(fname, section_times, labels):
    '''
    Write the horiz and vert sections timestamps for record.

    Keyword arguments:

    '''
    print "Saving section times..."
    print labels[0] + " [%lf:%lf]" %(section_times[0], section_times[1])
    print labels[1] + "Vertical [%lf:%lf]" %(section_times[2], section_times[3])
    
    fout = open(fname, "w")
    fout.write(labels[0] + " [%lf:%lf]\n" %(section_times[0], section_times[1]))
    fout.write(labels[1] + "Vertical [%lf:%lf]" %(section_times[2], section_times[3]))
    fout.close()
    
def write_data(orig_fname, section_fname, df):
    '''
    Write the horiz and vert sections for record.

    Keyword arguments:

    '''
    # read in the original header
    fin = open(orig_fname, "r")
    fout = open(section_fname, "w")
    # write out the original header
    fout.write(fin.readline())
    fout.write(fin.readline())
    fout.write(fin.readline())
    fout.write(fin.readline())
    fin.close()
    
    # write out the orientation sections
    index = df.index.tolist()
    for i in range(len(index)):
        fout.write(str(index[i]))
        fout.write(", ")
        
        row = df.iloc[i].tolist()
        for j in range(len(row) - 1):
            fout.write(str(row[j]))
            fout.write(", ")
        fout.write(str(row[len(row) - 1]))
        fout.write("\n")
    fout.close()
    
    
    