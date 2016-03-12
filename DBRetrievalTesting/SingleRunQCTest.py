'''
Created on 27 Nov 2015

@author: Sara
'''
import MySQLdb
import sys
import matplotlib.pyplot as pl
import matplotlib.pylab as pylab
import numpy as np
from scipy import stats
from sklearn import svm
import SupplementaryTools as st

#NOTE- possibly easier plotting function
import seaborn



# Open database connection- using a user that only has SELECT privileges to avoid accidentally dropping data
try:
    db = MySQLdb.connect("localhost",sys.argv[1],sys.argv[2], "ngsqc" ) #Pass username and password as command line arguments

except:
    sys.exit("Enter correct username and password!")
    
print "Successful connection"

# prepare a cursor object using cursor() method
cursor = db.cursor()

#Working on a single run
#Quality over Q30 over the cycle import
cursor.execute(""" SELECT QualByRow.MiSeqRunID,QualByRow.CycleID,
                    OverQ30 AS OverQ30
                    FROM QualByRow 
                    WHERE QualByRow.CycleID = QualByRow.CycleID
                    AND QualByRow.MiSeqRunID = '151106_M00766_0152_000000000-AJ5W5'
                    GROUP BY QualByRow.MiSeqRunID, QualByRow.CycleID, QualByRow.TileID """)
quality_over_cycle_all = cursor.fetchall()
print "Quality by Cycle Data Full Extracted"

quality_over_cycle_all_arr = np.asarray(quality_over_cycle_all)

xdata_q30 = quality_over_cycle_all_arr[:,1]
ydata_q30 = quality_over_cycle_all_arr[:,2]

#Import the supplementary tools class
s_tools = st.SupplementaryTools()

#Get the number of tiles
num_tiles = s_tools.locTileNo(quality_over_cycle_all_arr[:,1])

#quality_over_cycle_all_arr[0:num_tiles][:,2] #List of the first cycle

cycle_nos = s_tools.findCycleNos(quality_over_cycle_all_arr[:,1],num_tiles)
#print cycle_nos
num_cycles = max(cycle_nos)

#Means of the OverQ30 values per cycle
q30_arr_means = s_tools.findMeans(quality_over_cycle_all_arr,quality_over_cycle_all_arr[:,0],num_tiles)
#print arr_means

#Medians of the OverQ30 values per cycle
q30_arr_medians = s_tools.findMedians(quality_over_cycle_all_arr,quality_over_cycle_all_arr[:,0],num_tiles)

#Create an array of cycle numbers and array means- just to record the syntax for later
mean_arr = np.column_stack((cycle_nos,q30_arr_means))
#print mean_arr

q30_arr_stddv = s_tools.findStdDev(quality_over_cycle_all_arr,quality_over_cycle_all_arr[:,0],num_tiles)

q30_arr_iqr = s_tools.findIqr(quality_over_cycle_all_arr,quality_over_cycle_all_arr[:,0],num_tiles)


#Import the data to do the quality bins plots (and later statistics)
#Data already summed over whole run, not on a cycle by cycle basis here
cursor.execute(""" SELECT SQ01,SQ02,SQ03,SQ04,SQ05,SQ06,SQ07,SQ08,SQ09,SQ10,SQ11,SQ12,SQ13,SQ14,SQ15,SQ16,SQ17,
                    SQ18,SQ19,SQ20,SQ21,SQ22,SQ23,SQ24,SQ25,SQ26,SQ27,SQ28,SQ29,SQ30,SQ31,SQ32,SQ33,SQ34,SQ35,
                    SQ36,SQ37,SQ38,SQ39,SQ40,SQ41,SQ42,SQ43,SQ44,SQ45,SQ46,SQ47,SQ48,SQ49,SQ50
                    FROM BinnedQualities
                    WHERE BinnedQualities.MiSeqRunID = '151106_M00766_0152_000000000-AJ5W5' """)
run_binned_quality = cursor.fetchall()
print "Quality Data By Bin and Run Retrieved"

run_binned_quality_arr = np.asarray(run_binned_quality)


#Find the total number of clusters
total_clusters = run_binned_quality_arr.sum(axis=1)

#Obtain the binned quality data as a proportion, enables normalised comparison across runs
normalised_run_binned_quality_arr = run_binned_quality_arr / total_clusters[:,np.newaxis]

#NOTE: NOT NORMALISED AT PRESENT- Is this correct?
ydata_qb = run_binned_quality_arr[:,2]
#Known 50 quality bins
xdata_qb = np.arange(0,50)

#This might not work when scale up to more than one run- is a bit uninformative for a single run?
qd_arr_mean = np.mean(normalised_run_binned_quality_arr) #This works for a single run- one row of Quality bins per run
qd_arr_median = np.median(normalised_run_binned_quality_arr)
qd_arr_sd = np.std(normalised_run_binned_quality_arr)
qd_arr_iqr = (np.percentile(normalised_run_binned_quality_arr, 75, interpolation='higher')) - (np.percentile(normalised_run_binned_quality_arr, 25, interpolation='lower'))


#Import the data to do the intensity profiles
#Over cycle
cursor.execute(""" SELECT CycleID, Intensity_A, Intensity_C, Intensity_G, Intensity_T
                    FROM ExtractionMetrics
                        INNER JOIN GoodNemoData ON ExtractionMetrics.MiSeqRunID = GoodNemoData.MiSeqRunID
                    WHERE GoodNemoData.MiSeqRunID = '151106_M00766_0152_000000000-AJ5W5'
                    ORDER BY ExtractionMetrics.MiSeqRunID, ExtractionMetrics.CycleID  """)
intensity_cycles = cursor.fetchall()
print "Intensity for each base over cycle Retrieved"

#All intensity data for the run, but sorted by CycleID
intensity_cycles_arr = np.asarray(intensity_cycles)
A_int_c = intensity_cycles_arr[:,1]
C_int_c = intensity_cycles_arr[:,2]
G_int_c = intensity_cycles_arr[:,3]
T_int_c = intensity_cycles_arr[:,4]

#Retrieve summary metrics per cycle
#Base A over cycle
A_mean_c = s_tools.findMeans(intensity_cycles_arr,A_int_c,num_tiles,1)
A_med_c = s_tools.findMedians(intensity_cycles_arr,A_int_c,num_tiles,1)
A_sd_c = s_tools.findStdDev(intensity_cycles_arr,A_int_c,num_tiles,1)
A_iqr_c = s_tools.findIqr(intensity_cycles_arr,A_int_c,num_tiles,1)
#Base C over cycle
C_mean_c = s_tools.findMeans(intensity_cycles_arr,C_int_c,num_tiles,2)
C_med_c = s_tools.findMedians(intensity_cycles_arr,C_int_c,num_tiles,2)
C_sd_c = s_tools.findStdDev(intensity_cycles_arr,C_int_c,num_tiles,2)
C_iqr_c = s_tools.findIqr(intensity_cycles_arr,C_int_c,num_tiles,2)
#Base G over cycle
G_mean_c = s_tools.findMeans(intensity_cycles_arr,G_int_c,num_tiles,3)
G_med_c = s_tools.findMedians(intensity_cycles_arr,G_int_c,num_tiles,3)
G_sd_c = s_tools.findStdDev(intensity_cycles_arr,G_int_c,num_tiles,3)
G_iqr_c = s_tools.findIqr(intensity_cycles_arr,G_int_c,num_tiles,3)
#Base T over cycle
T_mean_c = s_tools.findMeans(intensity_cycles_arr,T_int_c,num_tiles,4)
T_med_c = s_tools.findMedians(intensity_cycles_arr,T_int_c,num_tiles,4)
T_sd_c = s_tools.findStdDev(intensity_cycles_arr,T_int_c,num_tiles,4)
T_iqr_c = s_tools.findIqr(intensity_cycles_arr,T_int_c,num_tiles,4) 

#Find the number of x datapoints for a single y value- (note here this is the same as the number of tiles)
num_x_cycles = len(intensity_cycles_arr)/num_cycles

#Create a suitable array of x values of the same length as the y values- for plotting
x_cycle_arr = s_tools.getXArray(cycle_nos,num_x_cycles)

#Over tile- don't need this second query- see results from Investigations.py for a different way to implement
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

#Create an array of the number of tiles analagous to 'cycle_nos' for cycles
tile_nos = range(1,(num_tiles+1)) #Python is 0-indexed


#Create a suitable array of x values of the same length as the y values- for plotting
x_tiles_arr = s_tools.getXArray(tile_nos,num_x_tiles)

#Extract cluster density
cursor.execute(""" SELECT TileMetrics.TileID, TileMetrics.Value/1000 AS ClusterDensity
                    FROM TileMetrics
                        INNER JOIN GoodNemoData ON TileMetrics.MiSeqRunID = GoodNemoData.MiSeqRunID
                    WHERE TileMetrics.CodeID = '100'
                    AND GoodNemoData.MiSeqRunID = '151106_M00766_0152_000000000-AJ5W5'
                    ORDER BY TileMetrics.MiSeqRunID, TileMetrics.TileID """)
cluster_density_full = cursor.fetchall()
print "Cluster Density Data Full Extracted"

cluster_density_full_arr = np.asarray(cluster_density_full)
tile_ids = cluster_density_full_arr[:,0]
cluster_densities = cluster_density_full_arr[:,1]

cluster_density_mean = np.mean(cluster_densities)
cluster_density_median = np.median(cluster_densities)
cluster_density_std = np.std(cluster_densities)
cluster_density_iqr = (np.percentile(cluster_densities, 75, interpolation='higher')) - (np.percentile(cluster_densities, 25, interpolation='lower'))

tile_ids = np.asarray(tile_ids)

#np.savetxt("C:\Users\Admin\Dropbox\Bioinformatics Clinical Science\MScProject\PlayingWithExcelData\Inspect5.csv",cluster_density_full_arr,delimiter=",")

cursor.execute(""" SELECT TileMetrics.TileID, TileMetrics.Value/1000 AS ClusterDensityPF
                    FROM TileMetrics
                        INNER JOIN GoodNemoData ON TileMetrics.MiSeqRunID = GoodNemoData.MiSeqRunID
                    WHERE TileMetrics.CodeID = '101'
                    AND GoodNemoData.MiSeqRunID = '151106_M00766_0152_000000000-AJ5W5'
                    ORDER BY TileMetrics.MiSeqRunID, TileMetrics.TileID """)
cluster_density_PF_full = cursor.fetchall()
print "Cluster Density Passing Filter Data Full Extracted"

cluster_density_PF_full_arr = np.asarray(cluster_density_PF_full)
cluster_densities_PF = cluster_density_PF_full_arr[:,1]

cluster_density_PF_mean = np.mean(cluster_densities_PF)
cluster_density_PF_median = np.median(cluster_densities_PF)
cluster_density_PF_std = np.std(cluster_densities_PF)
cluster_density_PF_iqr = (np.percentile(cluster_densities_PF, 75, interpolation='higher')) - (np.percentile(cluster_densities_PF, 25, interpolation='lower'))


#Work out percentage cluster passing filter
proportion_PF = np.divide(cluster_densities_PF,cluster_densities)

proportion_PF_mean = np.mean(proportion_PF)
proportion_PF_median = np.median(proportion_PF)
proportion_PF_std = np.std(proportion_PF)
proportion_PF_iqr = (np.percentile(proportion_PF, 75, interpolation='higher')) - (np.percentile(proportion_PF, 25, interpolation='lower'))


#Retrieve % aligned to PhiX (will be 0 for runs where no PhiX control was used)
#300 will be read 1, 301 read 2, 302 read 3, 303, read 4 etc
cursor.execute(""" SELECT TileMetrics.CodeID, TileMetrics.TileID, TileMetrics.Value AS AlignedPhiX
                    FROM TileMetrics
                        INNER JOIN GoodNemoData ON TileMetrics.MiSeqRunID = GoodNemoData.MiSeqRunID
                    WHERE TileMetrics.CodeID LIKE '30_'
                    AND GoodNemoData.MiSeqRunID = '151106_M00766_0152_000000000-AJ5W5'
                    GROUP BY TileMetrics.MiSeqRunID, TileMetrics.CodeID, TileMetrics.TileID """)
aligned_phix_full = cursor.fetchall()
print "Aligned % to PhiX Data Full Extracted"

aligned_phix_full_arr = np.asarray(aligned_phix_full)
aligned_phix = aligned_phix_full_arr[:,2]

aligned_phix_mean = np.mean(aligned_phix)
aligned_phix_median = np.median(aligned_phix)
aligned_phix_std = np.std(aligned_phix)
aligned_phix_iqr = (np.percentile(aligned_phix, 75, interpolation='higher')) - (np.percentile(aligned_phix, 25, interpolation='lower'))


#np.savetxt("C:\Users\Sara\Dropbox\Bioinformatics Clinical Science\MScProject\PlayingWithExcelData\Inspect6.csv",aligned_phix_full_arr,delimiter=",")

#Number of reads from each sample- I can't see any reason currently not to retrieve this data already binned
cursor.execute(""" SELECT IndexMetricsMSR.MiSeqRunID, IndexMetricsMSR.SampleName, SUM(NumControlClusters) AS ClustersPerSample
                    FROM IndexMetricsMSR
                        INNER JOIN GoodNemoData ON IndexMetricsMSR.MiSeqRunID = GoodNemoData.MiSeqRunID
                    WHERE GoodNemoData.MiSeqRunID = '151106_M00766_0152_000000000-AJ5W5'
                    GROUP BY IndexMetricsMSR.MiSeqRunID, IndexMetricsMSR.SampleName  """)
reads_per_sample = cursor.fetchall()
print "Number of Reads per Sample Data Extracted"

reads_per_sample_arr = np.asarray(reads_per_sample)

#How many reads per run- old way not incorporating undetermined reads
'''
cursor.execute(""" SELECT IndexMetricsMSR.MiSeqRunID, SUM(NumControlClusters) AS ClustersPerRun
                    FROM IndexMetricsMSR
                        INNER JOIN GoodNemoData ON IndexMetricsMSR.MiSeqRunID = GoodNemoData.MiSeqRunID
                    WHERE GoodNemoData.MiSeqRunID = '151106_M00766_0152_000000000-AJ5W5'
                    GROUP BY IndexMetricsMSR.MiSeqRunID """)
reads_per_run = cursor.fetchall()
print "Number of Reads per Run Data Extracted"
'''
#How many reads per run- new way that is correct extracting from tile metrics
cursor.execute(""" SELECT TileMetrics.MiSeqRunID, SUM(Value) AS ClustersPerRun
                    FROM TileMetrics
                        INNER JOIN GoodNemoData ON TileMetrics.MiSeqRunID = GoodNemoData.MiSeqRunID
                    WHERE GoodNemoData.MiSeqRunID = '151106_M00766_0152_000000000-AJ5W5'
                    AND TileMetrics.CodeID = '103'
                    GROUP BY TileMetrics.MiSeqRunID """)
reads_per_run = cursor.fetchall()
print "Number of Reads per Run Data Extracted"


reads_per_run_arr = np.asarray(reads_per_run)

#Calculate proportion of reads from each sample (i.e. normalised to number of reads)
#This function assumes that the MiSeq ID is stored in column 0
runs_sample_divisor = s_tools.outputRunReadsPerSample(reads_per_sample_arr,reads_per_run_arr,1)

#!!!!!!!!!FIX HERE- this is a proportion of total reads whereas the SAV viewer does as a proportion of reads passing filter!!!!!!!!!
#FIXED- changed data extract above
proportion_of_reads_sample = np.divide(reads_per_sample_arr[:,2],runs_sample_divisor)

print reads_per_sample_arr[:,1]
print proportion_of_reads_sample

mean_reads_sample = np.mean(proportion_of_reads_sample)
median_reads_sample = np.median(proportion_of_reads_sample)
std_reads_sample = np.std(proportion_of_reads_sample)
iqr_reads_sample = (np.percentile(proportion_of_reads_sample, 75, interpolation='higher')) - (np.percentile(proportion_of_reads_sample, 25, interpolation='lower'))

print mean_reads_sample
print median_reads_sample
print std_reads_sample
print iqr_reads_sample

#Identification of outliers- rough method (modified Thompson Tau test)
#To determine if a value is an outlier: Calculate (X - mean(X)) / s. . If > Rejection Region, the data point is an outlier.

#Define an outlier as 3 standard deviations from the mean (worry about reference later)
#3 was too far it went into negative below- try 2 sd from the mean
print mean_reads_sample + (2*std_reads_sample)
print mean_reads_sample - (2*std_reads_sample)

print mean_reads_sample + (1*std_reads_sample)
print mean_reads_sample - (1*std_reads_sample)

import GrubbsOutliers
print "here is the output of the Grubbs test"
grubbs_result = GrubbsOutliers.Grubbs_outlier_test(proportion_of_reads_sample, 0.95)
#From here need to work out the samples that differ from the critical value and then how to read them out.
#Note that this is probably not sensitive enough as it looks like it won't pick up 15M11860 which looks low

print grubbs_result
print grubbs_result[(len(grubbs_result)-1)]
print grubbs_result[(len(grubbs_result)-3)]

grubbs_crit_val = grubbs_result[(len(grubbs_result)-3)]

grubbs_just_results = grubbs_result[0]
print grubbs_just_results


for index, entry in enumerate(grubbs_just_results):
    if entry > grubbs_crit_val:
        print index
        print reads_per_sample_arr[index,1]
        print proportion_of_reads_sample[index]
        print entry
#< 


#http://db-pub.com/news-10018307/outlier-detection-with-sql-server-part-4-peirce-s-criterion.html


#np.savetxt("C:\Users\Sara\Dropbox\Bioinformatics Clinical Science\MScProject\PlayingWithExcelData\Inspect2.csv",normalised_run_binned_quality_arr, delimiter=",")


#Plot all data
#First retrieval
pl.figure(1)
Figure1 = pl.plot(xdata_q30,ydata_q30)

pl.figure(2)
Figure2 = pl.plot(cycle_nos,q30_arr_means)
Figure2 = pl.plot(cycle_nos,q30_arr_medians) # Less sensitive to outliers

pl.figure(3)
Figure3 = pl.plot(cycle_nos,q30_arr_stddv)
Figure3 = pl.plot(cycle_nos,q30_arr_iqr)

pl.show()

#'''
#Second retrieval
#Plotting the non-normalised results here- to swap that over, just plot from the other array (as figure 5)
#This shows the variability with the runs along the x axis
pl.figure(4)
Figure4 = pl.plot(xdata_qb,run_binned_quality_arr[:,:].T)

pl.figure(5)
Figure5 = pl.plot(xdata_qb,normalised_run_binned_quality_arr[:,:].T)


#Third retrieval
#Shows intensity profile along cycle- full data (all data points)
pl.figure(6)
Figure6 = pl.plot(intensity_cycles_arr)

#Need to fix the scaling on these plots- want to plot all from same cycle in same bin- fixed!
pl.figure(7)
pylab.title("Intensity Over Cycle Every Value")
#pylab.xlim([0,308])
Figure7a_e = pl.plot(A_int_c)
Figure7c_e =pl.plot(C_int_c)
Figure7g_e = pl.plot(G_int_c)
Figure7t_e = pl.plot(T_int_c)

pl.figure(8)
Figure8 = pl.plot(x_cycle_arr,intensity_cycles_arr)

pl.figure(9)
pylab.title("Intensity Over Cycle")
Figure7a = pl.plot(x_cycle_arr,A_int_c)
Figure7c =pl.plot(x_cycle_arr,C_int_c)
Figure7g = pl.plot(x_cycle_arr,G_int_c)
Figure7t = pl.plot(x_cycle_arr,T_int_c)

#Shows intensity profile over tiles- full data (all data points)
pl.figure(10)
Figure10 = pl.plot(intensity_tiles_arr) #I have no idea what this is trying to show

pl.figure(11)
Figure11 = pl.plot(x_tiles_arr,intensity_tiles_arr)

pl.figure(12)
pylab.title("Intensity Over Tile")
Figure12 = pl.plot(x_tiles_arr,A_int_t)

#Plot separated bottom and top surface to try and figure out what is going on in the above plot- left for now

pl.figure(13)
Figure13 = pl.plot(cluster_density_full_arr)

pl.figure(14)
pylab.title("Cluster Density Per Tile")
#print cluster_densities
#print len(cluster_densities)
#ax = pl.axes()
Figure14 = pl.plot(tile_nos,cluster_densities)
#ax.set_xticks(tile_ids)

#tick_locs = ax.xaxis.get_majorticklocs()
#print tick_locs
#ax.xaxis.set_ticks(tile_ids)

#locs, labels = pl.xticks()
#print locs
#print tile_ids
#pl.xticks(locs, tile_ids)
pl.xticks(tile_nos, tile_ids)

pl.figure(15)
Figure15 = pl.plot(cluster_density_PF_full_arr)

pl.figure(16)
pylab.title("Cluster Density Passing Filter Per Tile")
Figure16 = pl.plot(tile_nos,cluster_densities_PF)
pl.xticks(tile_nos, tile_ids)

pl.figure(17)
pylab.title("Cluster Densities Per Tile Total and Passing Filter")
pl.plot(tile_nos,cluster_densities)
pl.xticks(tile_nos, tile_ids)
pl.plot(tile_nos,cluster_densities_PF)
pl.xticks(tile_nos, tile_ids)

pl.figure(18)
pylab.title("Percentage Clusters Passing Filter Per Tile")
perc_PF = proportion_PF*100
pl.plot(tile_nos,perc_PF)
pl.xticks(tile_nos, tile_ids)

pl.figure(19)
pylab.title("% Aligned to PhiX Read 1")
pl.plot(tile_nos,aligned_phix[0:(len(tile_nos))])
pl.xticks(tile_nos, tile_ids)

pl.figure(20)
pylab.title("% Aligned to PhiX Read 2")
pl.plot(tile_nos,aligned_phix[(len(tile_nos)):(len(aligned_phix))])
pl.xticks(tile_nos, tile_ids)
#print aligned_phix[(len(aligned_phix)-1)]
#print aligned_phix[0:(len(tile_nos))]
#print aligned_phix[(len(tile_nos)):(len(aligned_phix))]






#pl.show()
#'''



#'''
cursor.execute(""" SELECT QualByRow.MiSeqRunID,QualByRow.CycleID,
                    AVG(OverQ30) AS AOverQ30
                    FROM QualByRow 
                    WHERE QualByRow.CycleID = QualByRow.CycleID
                    AND QualByRow.MiSeqRunID = '151106_M00766_0152_000000000-AJ5W5'
                    GROUP BY QualByRow.MiSeqRunID, QualByRow.CycleID """)
quality_over_cycle = cursor.fetchall()
print "Quality by Cycle Data Extracted"

quality_over_cycle_arr = np.asarray(quality_over_cycle)

xdata = quality_over_cycle_arr[:,1]
ydata = quality_over_cycle_arr[:,2]

#Plot of the average Q score over the cycle
pl.figure(1)
Figure = pl.plot(xdata,ydata)

#Plot of the range of q score across the cycle?


pl.show()
#'''





