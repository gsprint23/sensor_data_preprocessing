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

OrientationFiltering --- utils.py
Created on Apr 2, 2015

Dependencies:
Matplotlib

@author: Gina Sprint (with help from Vladimir Borisov)
'''

import matplotlib.pyplot as plt


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

def plot_acceleration_data(df, sensor_loc, fname=None, section_times=None):
    '''
    Plot the acceleration so the user can find the horiz and vert sections.

    Keyword arguments:

    '''
    plt.figure()  
    plt.plot(df.index, df['Wide Range Accelerometer X'], label = 'X-axis') 
    plt.plot(df.index, df['Wide Range Accelerometer Y'], label = 'Y-axis') 
    plt.plot(df.index, df['Wide Range Accelerometer Z'], label = 'Z-axis')   
    
    if section_times is not None:
        plt.axvspan(section_times[0], section_times[1], facecolor='b', alpha=0.5) 
        plt.text(section_times[0], -11, "Horizontal", style='italic', bbox={'facecolor':'b', 'alpha':0.8, 'pad':10})
        
        plt.axvspan(section_times[2], section_times[3], facecolor='g', alpha=0.5)
        plt.text(section_times[2], -11, "Vertical", style='italic', bbox={'facecolor':'g', 'alpha':0.8, 'pad':10}) 
 
    plt.xlabel('Timestamp')
    plt.ylabel('Acceleration [m/s^2]')
    plt.title('Sensor location: %s' %(sensor_loc))
    plt.legend()
    if fname is not None:
        plt.savefig(fname)
    plt.show()   
    
    
def write_notes(fname, section_times):
    '''
    Write the horiz and vert sections timestamps for record.

    Keyword arguments:

    '''
    print "Saving section times..."
    print "Horizontal [%lf:%lf]" %(section_times[0], section_times[1])
    print "Vertical [%lf:%lf]" %(section_times[2], section_times[3])
    
    fout = open(fname, "w")
    fout.write("Horizontal [%lf:%lf]\n" %(section_times[0], section_times[1]))
    fout.write("Vertical [%lf:%lf]" %(section_times[2], section_times[3]))
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
    
    
    