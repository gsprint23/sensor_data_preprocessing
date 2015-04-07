sensor_data_preprocessing
==========================

sensor_data_preprocessing is a code base used to orient and filter Shimmer sensors  &lt;http://www.shimmersensing.com/>. The code also trims the data files down to the sections of interest. This code is highly specific to 

sensor_data_preprocessing 1.0.0
------------
https://github.com/gsprint23

sensor_data_preprocessing is Copyright (C) 2015 Gina L. Sprint
Email: Gina Sprint <gsprint@eecs.wsu.edu>

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
