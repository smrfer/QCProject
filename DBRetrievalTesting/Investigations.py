'''
Created on 1 Dec 2015

@author: Sara
'''
import MySQLdb
import sys
import matplotlib.pyplot as pl
import matplotlib.pylab as pylab
import numpy as np
from scipy import stats
import pandas as pd
import SupplementaryTools as st

#A priori kmown for this data (saves a separate import)
num_cycles = 308
cycle_nos = range(1,(num_cycles+1)) #Python is 0-indexed
num_tiles = 28
tile_nos = range(1,(num_tiles+1)) #Python is 0-indexed




#Import the supplementary tools class
s_tools = st.SupplementaryTools()

# Open database connection- using a user that only has SELECT privileges to avoid accidentally dropping data
try:
    db = MySQLdb.connect("localhost",sys.argv[1],sys.argv[2], "ngsqc" ) #Pass username and password as command line arguments

except:
    sys.exit("Enter correct username and password!")
    
print "Successful connection"




cursor = db.cursor()

#Over tile
cursor.execute(""" SELECT TileID, Intensity_A, Intensity_C, Intensity_G, Intensity_T
                    FROM ExtractionMetrics
                        INNER JOIN GoodNemoData ON ExtractionMetrics.MiSeqRunID = GoodNemoData.MiSeqRunID
                    WHERE GoodNemoData.MiSeqRunID = '151106_M00766_0152_000000000-AJ5W5' 
                    ORDER BY ExtractionMetrics.MiSeqRunID,ExtractionMetrics.TileID  """)
intensity_tiles = cursor.fetchall()
print "Intensity for each base over tile Retrieved"

#All intensity data for the run, but sorted by TileID
intensity_tiles_arr = np.asarray(intensity_tiles)
A_int_t = intensity_tiles_arr[:,1]
C_int_t = intensity_tiles_arr[:,2]
G_int_t = intensity_tiles_arr[:,3]
T_int_t = intensity_tiles_arr[:,4]

#Retrieve summary metrics per cycle
#print num_cycles
#Base A over tile
A_mean_t = s_tools.findMeans(intensity_tiles_arr,A_int_t,num_cycles,1)
A_med_t = s_tools.findMedians(intensity_tiles_arr,A_int_t,num_cycles,1)
A_sd_t = s_tools.findStdDev(intensity_tiles_arr,A_int_t,num_cycles,1)
A_iqr_t = s_tools.findIqr(intensity_tiles_arr,A_int_t,num_cycles,1)
print A_mean_t
#Base C over tile
C_mean_t = s_tools.findMeans(intensity_tiles_arr,C_int_t,num_cycles,2)
C_med_t = s_tools.findMedians(intensity_tiles_arr,C_int_t,num_cycles,2)
C_sd_t = s_tools.findStdDev(intensity_tiles_arr,C_int_t,num_cycles,2)
C_iqr_t = s_tools.findIqr(intensity_tiles_arr,C_int_t,num_cycles,2)
#Base G over tile
G_mean_t = s_tools.findMeans(intensity_tiles_arr,G_int_t,num_cycles,3)
G_med_t = s_tools.findMedians(intensity_tiles_arr,G_int_t,num_cycles,3)
G_sd_t = s_tools.findStdDev(intensity_tiles_arr,G_int_t,num_cycles,3)
G_iqr_t = s_tools.findIqr(intensity_tiles_arr,G_int_t,num_cycles,3)
#Base T over tile
T_mean_t = s_tools.findMeans(intensity_tiles_arr,T_int_t,num_cycles,4)
T_med_t = s_tools.findMedians(intensity_tiles_arr,T_int_t,num_cycles,4)
T_sd_t = s_tools.findStdDev(intensity_tiles_arr,T_int_t,num_cycles,4)
T_iqr_t = s_tools.findIqr(intensity_tiles_arr,T_int_t,num_cycles,4) 

#Find the number of x datapoints for a single y value- (note here this is the same as the number of tiles)
num_x_tiles = len(intensity_tiles_arr)/num_tiles

#Create a suitable array of x values of the same length as the y values- for plotting
x_tiles_arr = s_tools.getXArray(tile_nos,num_x_tiles)

print A_int_t
print A_sd_t

#Find max of each cycle and normalise wrt to it- make easier to identify badly performing tiles on a cycle
cursor.execute(""" SELECT TileID, CycleID, Intensity_A, Intensity_C, Intensity_G, Intensity_T
                    FROM ExtractionMetrics
                        INNER JOIN GoodNemoData ON ExtractionMetrics.MiSeqRunID = GoodNemoData.MiSeqRunID
                    WHERE GoodNemoData.MiSeqRunID = '151106_M00766_0152_000000000-AJ5W5'
                    ORDER BY ExtractionMetrics.MiSeqRunID,ExtractionMetrics.CycleID  """)
intensity = cursor.fetchall()
print "Extreme new Query executed"

intensity_arr = np.asarray(intensity)

#Get maximum of each cycle and normalise numbers for each cycle to this value
A_arr = s_tools.getNormIntOverCycle(intensity_arr,intensity_arr[:,2],num_tiles,2)
C_arr = s_tools.getNormIntOverCycle(intensity_arr,intensity_arr[:,3],num_tiles,3)
G_arr = s_tools.getNormIntOverCycle(intensity_arr,intensity_arr[:,4],num_tiles,4)
T_arr = s_tools.getNormIntOverCycle(intensity_arr,intensity_arr[:,5],num_tiles,5)

#First two columns stay the same
tile_id = intensity_arr[:,0]
cycle_id = intensity_arr[:,1]      

#Make an array with this new data for sorting and then plotting       
norm_int_arr = np.column_stack((intensity_arr[:,0],intensity_arr[:,1],A_arr,C_arr,G_arr,T_arr))

#np.savetxt("C:\Users\Sara\Dropbox\Bioinformatics Clinical Science\MScProject\PlayingWithExcelData\Inspect3.csv",norm_int_arr,delimiter=",")

#Sort the array by tile number
#norm_int_arr_sort = norm_int_arr.sort(axis=,kind='mergesort')
data_frame = pd.DataFrame(data=norm_int_arr)
norm_int_data_frame_sort = data_frame.sort_values([0,1,2,3,4,5],axis=0)

norm_int_arr_sort = norm_int_data_frame_sort.as_matrix()

#np.savetxt("C:\Users\Sara\Dropbox\Bioinformatics Clinical Science\MScProject\PlayingWithExcelData\Inspect4.csv",norm_int_arr_sort,delimiter=",")

#'''
pl.figure
pylab.title("Intensity Over Tile")
Figure = pl.plot(x_tiles_arr,A_int_t)

pl.show()
#'''
