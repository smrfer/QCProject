'''
Created on Jan 6, 2016

@author: Sara
'''
#Required imports
from __future__ import print_function
import MySQLdb
import sys
import warnings
import numpy as np
import scipy.stats as stat
import matplotlib.pyplot as pl
import re

#Load in a bunch of runs
#Later on this will trigger from Matt's transfer programme

#Connect to the database- user with select privileges only
try:
    db = MySQLdb.connect("localhost",sys.argv[1],sys.argv[2], "ngsqc" ) #Pass username and password as command line arguments

except:
    sys.exit("Enter correct username and password!")
    
print("Successful connection")

cursor = db.cursor()

#Extract all the runs in the database
cursor.execute(""" SELECT MiSeqRun.MiSeqRunID
                    FROM MiSeqRun """)
runs_in_db = cursor.fetchall()
print("List of runs extracted")

#Make a text file containing all these runs- let it create in base folder
#print(os.getcwd())
#outfile = (os.getcwd()+"\\runs.txt")
outpath = sys.path[0]
outpath = outpath + "\\runs.txt"
#print(outpath)

outfile = open(outpath, 'w')

for run in runs_in_db:
    #print(x[0])
    print (run[0], file = outfile)
print("List of runs generated")
outfile.close()

#Just for now use this as an example run- last run
run_for_import = run[0]
print(run_for_import)

'''
#Testing loading a single run
sql_command = """ SELECT *
                    FROM MiSeqRun
                    WHERE MiSeqRun.MiSeqRunID = """ + "'" + run_for_import + "'"
cursor.execute(sql_command)
current_run = cursor.fetchall()
print("List of runs extracted")
'''

#How long is each read?
sql_command = """ SELECT ReadNumber, NumberOfCycles, Indexed
                    FROM Rds INNER JOIN LinkMiSeqRunRds
                    ON Rds.ReadID = LinkMiSeqRunRds.ReadID
                    WHERE LinkMiSeqRunRds.MiSeqRunID = """ + "'" + run_for_import + "'"
cursor.execute(sql_command)
reads_info = cursor.fetchall()
reads_info_arr = np.array(reads_info)
#Convert array from string type to integer type
reads_info_arr_int = reads_info_arr.astype(int)
#print(reads_info)
#print(reads_info_arr)
#print(reads_info_arr[:,1])

ind_reads = 0

for ind,read_extract in enumerate(reads_info_arr_int):   
    if read_extract[2] == 0:
        #Read is not an index read
        #print(read_extract[1])
        if (ind == 1) and (read_extract[1] == reads_info_arr_int[:,1].max()):
            #R1 is the first one
            read1_length = read_extract[1]
        elif (ind != 1) and (read_extract[1] == reads_info_arr_int[:,1].max()):
            #R2 is the last one
            read2_length = read_extract[1]
    elif read_extract[2] == 1:
        ind_reads += read_extract[1]
    else:
        raise Exception("Read is not properly identified as either not index or an index read")
    
#How many reads there are from this way of counting them (all index reads and R1 and R2)
num_cycles_reads = sum(reads_info_arr_int[:,1])

#Is the run complete?
sql_command = """ SELECT MAX(ExtractionMetrics.CycleID)
                    FROM ExtractionMetrics
                    WHERE ExtractionMetrics.MiSeqRunID = """ + "'" + run_for_import + "'"
cursor.execute(sql_command)
current_run_extracted = cursor.fetchall()[0][0]
print("Extracted")
#print(current_run_extracted)

sql_command = """ SELECT MAX(CorrectedIntMetrics.CycleID)
                    FROM CorrectedIntMetrics
                    WHERE CorrectedIntMetrics.MiSeqRunID = """ + "'" + run_for_import + "'"
cursor.execute(sql_command)
current_run_called = cursor.fetchall()[0][0]
print("Called")
#print(current_run_called)

sql_command = """ SELECT MAX(QualityMetrics.CycleID)
                    FROM QualityMetrics
                    WHERE QualityMetrics.MiSeqRunID = """ + "'" + run_for_import + "'"
cursor.execute(sql_command)
current_run_scored = cursor.fetchall()[0][0]
print("Scored")
#print(current_run_scored)

#Tests to ensure that the wrong bit will trigger- do one at a time
#current_run_extracted = 2 #Pass test
#current_run_called = 2 #Pass test
#current_run_scored = 2 #Pass test

##Is the run complete
##Check that the total number of extracted matches the number of cycles from the reads- if not then there's a problem
assert current_run_extracted  == num_cycles_reads
##Are the extracted, called and scored numbers equal? i.e. is run analysis complete
if current_run_extracted == current_run_called == current_run_scored:
    print("All OK")
else:
    print("Run " + str(run_for_import) + " incomplete")

##Extract version number of reagents
cursor.execute(""" SELECT MiSeqRun.KitVersionNumber
                    FROM MiSeqRun
                    WHERE MiSeqRun.MiSeqRunID = """ + "'" + run_for_import + "'")
kit_version = cursor.fetchall()[0][0]

#Create a dictionary with threshold cluster densities for reagent version numbers
#Values outside of these should generate a warning
#Source: MiSeq specifications page from Illumina
threshold_dens = {"2":(865,965),"3":(1200,1400)}
#Set an outside value exceeding which generates an error
outside_threshold_dens = {"2":(700,1100),"3":(1100,1600)}
    
##Cluster density
cursor.execute(""" SELECT TileMetrics.TileID, TileMetrics.Value/1000 AS ClusterDensity
                    FROM TileMetrics
                    WHERE TileMetrics.CodeID = '100'
                    AND TileMetrics.MiSeqRunID = """ + "'" + run_for_import + "'")
cluster_density_full = cursor.fetchall()
cluster_density_full_arr = np.array(cluster_density_full)
print("Cluster Density Data Full Extracted")
mean_dens = (np.mean(cluster_density_full_arr[:,1]))
max_dens = (np.max(cluster_density_full_arr[:,1]))
min_dens = (np.min(cluster_density_full_arr[:,1]))
std_dens = (np.std(cluster_density_full_arr[:,1])) # This default does across axis=0 which is correct
median_dens = (np.median(cluster_density_full_arr[:,1]))
#print(std_dens)

#print out the cluster density
#print(str(mean_dens) + " +/- " + str(std_dens))

##Cluster density passing filter
cursor.execute(""" SELECT TileMetrics.TileID, TileMetrics.Value/1000 AS ClusterDensity
                    FROM TileMetrics
                    WHERE TileMetrics.CodeID = '101'
                    AND TileMetrics.MiSeqRunID = """ + "'" + run_for_import + "'")
cluster_density_full_pf = cursor.fetchall()
cluster_density_full_pf_arr = np.array(cluster_density_full_pf)
print("Cluster Density Data Full Passing Filter Extracted")
mean_dens_pf = (np.mean(cluster_density_full_pf_arr[:,1]))
std_dens_pf = (np.std(cluster_density_full_pf_arr[:,1]))
median_dens_pf = (np.median(cluster_density_full_pf_arr[:,1]))

#Retrieve the values associated with the kit version
threshold_vals = threshold_dens.get(str(kit_version),None)
outside_threshold_vals = outside_threshold_dens.get(str(kit_version),None)
#print(threshold_vals)
#print(outside_threshold_vals)
'''
#Testing values
#mean_dens_pf = 750
#mean_dens_pf = 650
#mean_dens_pf = 1000
#mean_dens_pf = 1200
'''

cluster_d = str("%.2f" %mean_dens_pf)
kt = str(kit_version)

#Checks for thresholding levels on cluster density
if (mean_dens_pf < outside_threshold_vals[0]):
    raise Exception("Cluster density very low at "+ cluster_d + " on a v" + kt + " kit")
elif (mean_dens_pf > outside_threshold_vals[1]):
    raise Exception("Cluster density very high at "+ cluster_d + " on a v" + kt + " kit")
elif (mean_dens_pf < threshold_vals[0]):
    #outside Illumina recommended thresholds
    warnings.warn("Cluster density is low at " + cluster_d + " on a v" + kt + " kit")
elif (mean_dens_pf > threshold_vals[1]):
    #outside Illumina recommended thresholds
    warnings.warn("Cluster density is high at " + cluster_d + " on a v" + kt + " kit")

#Is there a big range in the cluster density?- this is over tiles and could indicate a problem with a tile
#To use std dev or iqr? Start with std dev
#Threshold for standard deviation
#print((std_dens/mean_dens)*100) # This is the % of the mean that falls within 1 standard deviation
#What is a high amount of % of the mean to fall outside of 1sd?
#Set std threshold to that
std_threshold = float(mean_dens)*0.05 #Pick the correct threshold value (gone for 5% of the mean here)
#print(mean_dens)
#print(float(mean_dens))
#print((std_dens/mean_dens))
#print(float(mean_dens)*0.018159995802775248)
#print(float(mean_dens)*0.05)
#print(std_dens)
if ((std_dens/mean_dens)*100) > std_threshold: 
    print("Large range in cluster densities. Possible issue with a tile.")

#Is there a big gap between cluster density and cluster density passing filter?
#If they are doing boxplots then it should be based on the median
perc_diff_med_cd = (median_dens_pf/median_dens*100)
#Working out a useful threshold- where would median be if was at a value of 'x'- here 85
#print((float(85)/float(100))*float(median_dens))

if perc_diff_med_cd < 85: #Is this a useful threshold?
    print("Low number of clusters passing filter")

##Number/Proportion of bases >Q30
cursor.execute(""" SELECT (SUM(Q30)+SUM(Q31)+SUM(Q32)+SUM(Q33)+SUM(Q34)+SUM(Q35)
                    +SUM(Q36)+SUM(Q37)+SUM(Q38)+SUM(Q39)+SUM(Q40)+SUM(Q41)+SUM(Q42)+SUM(Q43)
                    +SUM(Q44)+SUM(Q45)+SUM(Q46)+SUM(Q47)+SUM(Q48)+SUM(Q49)+SUM(Q50)) /
                    (SUM(Q01)+SUM(Q02)+SUM(Q03)+SUM(Q04)+SUM(Q05)+SUM(Q06)+SUM(Q07)+SUM(Q08)+
                    SUM(Q09)+SUM(Q10)+SUM(Q11)+SUM(Q12)+SUM(Q13)+SUM(Q14)+SUM(Q15)+SUM(Q16)+
                    SUM(Q17)+SUM(Q18)+SUM(Q19)+SUM(Q20)+SUM(Q21)+SUM(Q22)+SUM(Q23)+SUM(Q24)+
                    SUM(Q25)+SUM(Q26)+SUM(Q27)+SUM(Q28)+SUM(Q29)+SUM(Q30)+SUM(Q31)+SUM(Q32)+
                    SUM(Q33)+SUM(Q34)+SUM(Q35)+SUM(Q36)+SUM(Q37)+SUM(Q38)+SUM(Q39)+SUM(Q40)+
                    SUM(Q41)+SUM(Q42)+SUM(Q43)+SUM(Q44)+SUM(Q45)+SUM(Q46)+SUM(Q47)+SUM(Q48)+
                    SUM(Q49)+SUM(Q50))
                    FROM QualityMetrics
                    WHERE QualityMetrics.MiSeqRunID = """ + "'" + run_for_import + "'")
qual_metrics_Q30 = cursor.fetchall()
qual_over_Q30 = qual_metrics_Q30[0][0]
#print(qual_over_Q30)

'''
#Testing
qual_over_Q30 = 0.88
qual_over_Q30 = 0.78
'''

if qual_over_Q30 < 0.85:
    raise Exception("Only " + str("%.0f" %(qual_over_Q30*100)) + "% of bases over Q30")
elif qual_over_Q30 < 0.90:
    warnings.warn("Fewer than 90% of bases are over Q30")

    
#Look at reads separately- WIP
cursor.execute(""" SELECT *
                    FROM QualityMetrics
                    WHERE QualityMetrics.MiSeqRunID = """ + "'" + run_for_import + "'")
qual_metrics = cursor.fetchall()
qual_metrics_arr = np.asarray(qual_metrics)
#Number of columns in the quality metrics array
qual_num_cols = (len(qual_metrics_arr[0,:]))
#Number of rows in the quality metrics array
qual_num_rows = (len(qual_metrics_arr[:,0]))
#Create array excluding the MiSeqRunID (which cannot be force converted to an integer)
qual_metrics_arr_mod = np.concatenate((qual_metrics_arr[:,0:3],qual_metrics_arr[:,4:qual_num_cols]),axis=1)
#Force conversion of array to integer type (necessary as db driver retrieves strings)
qual_metrics_arr_mod_int = qual_metrics_arr_mod.astype(int)
#print(qual_metrics_arr_mod_int)

#Need to sort the data based on cycle if going to slice it later (3rd column)
qual_metrics_arr_mod_int_sorted = qual_metrics_arr_mod_int[qual_metrics_arr_mod_int[:,2].argsort()]
#print(qual_metrics_arr_mod_int_sorted)

#To split into separate reads based on number of cycles
#There is a cycle per each tile, which includes top and bottom surface (so 2*number of tiles)
#Obtain the number of tiles
cursor.execute(""" SELECT MiSeqRun.NumTiles
                    FROM MiSeqRun
                    WHERE MiSeqRunID = """ + "'" + run_for_import + "'")
num_tls = cursor.fetchall()[0][0]
#print(num_tls)
#print(read1_length)
#print(read2_length)

#This sums up all the values column-wise- could use to replace separate data extract above
#print(np.sum(qual_subs_arr_int, axis = 0))

#This sums up all the values row-wise- the different summed totals probably reflect the different reads
#This is of limited use if it is not sorted
#print(np.sum(qual_subs_arr_int, axis = 1))

'''
Testing sorting
a = np.array([[1,2,3],[1,4,5],[1,1,6]])
ab = a[a[:,1].argsort()]
print(a)
print(ab)
'''

#How the reads (without the index reads) extend
num_surfaces = 2
r1_end = num_surfaces*num_tls*read1_length
#read1
first_read_qual = qual_metrics_arr_mod_int_sorted[0:r1_end,:]
#read2
r2_start = r1_end + (ind_reads*num_surfaces*num_tls)
#print(ind_reads)
second_read_qual = qual_metrics_arr_mod_int_sorted[r2_start:qual_num_rows,:]

#Subset of array containing bins Q01-Q50 only- start from position 3 as started from the int array so
#MiSeqRunID has already been removed- this slicing has been tested to slice at the correct position
first_read_qual_subs =(first_read_qual[:,3:qual_num_cols])
second_read_qual_subs =(second_read_qual[:,3:qual_num_cols])

#print(np.sum(first_read_qual_subs,axis=0))
'''
#Check index of Q30 (checked against Excel spreadsheet)- it is at index 32 in the full array
print(first_read_qual)
print(first_read_qual[:,1:3]) #Get the tile and cycle number for comparison with the entry below
print(first_read_qual[:,32]) #Will be -3 in the substring- this is checked too- need full index to get correct entry in Excel sheet
#Check values match- they do
print(first_read_qual_subs[:,29])
'''

#Find the proportion of Q30 for the first read
Q30_r1_arr = first_read_qual_subs[:,29:len(first_read_qual_subs[0,:])]
Q30_r1 = (np.sum(Q30_r1_arr))
#print(Q30_r1) #This is correct checked against Excel spreadsheet
Qtotal_r1 = (np.sum(first_read_qual_subs))
#print(Qtotal_r1) #This is correct checked against Excel spreadsheet
prop_Q30_r1 = (float(Q30_r1)/float(Qtotal_r1))
print(prop_Q30_r1*100)

#Find the proportion of Q30 for the second read
Q30_r2_arr = second_read_qual_subs[:,29:len(second_read_qual_subs[0,:])]
Q30_r2 = (np.sum(Q30_r2_arr))
#print(Q30_r1) #This is correct checked against Excel spreadsheet
Qtotal_r2 = (np.sum(second_read_qual_subs))
#print(Qtotal_r1) #This is correct checked against Excel spreadsheet
prop_Q30_r2 = (float(Q30_r2)/float(Qtotal_r2))
print(prop_Q30_r2*100)

#Is there a big difference in >Q30 between r1 and r2?- Test for significance
#Just look to see if there is a difference in the spread of quality scores perhaps
#For this will need to create a 1D distribution across the range of quality scores
#We already have this with the first/second_read_qual_subs- just need to sum it over the correct axis
r1_qual_over_cycle = np.sum(first_read_qual_subs,axis=0)
r2_qual_over_cycle = np.sum(second_read_qual_subs,axis=0)

#Non-parametric, so use rank sum test (Wilcoxon?)
#There#s a fair chance that this test is meaningless as I've put in binned data and so the median will be 0
#Need to figure out a useful test for this kind of frequency data (TO DO)
'''
Use Mann Whitney for independent samples? Alternative is Kolmogorov-Smirnov.
Mann Whitney test deals better with ties (values that are the same and need to be converted into rank)
We have got a fair bit of tied data (all 0 values and huge numbers of values in same Q bin), so I prefer Mann-Whitney to K-S.
K-S is more sensitive to changes in shape of distribution etc though.
Have tried Chi-Sq and Fisher's exact test, but they can't be used because there's more than 2x2 (Fisher) and
The ChiSq test cannot be used because of the 0s in the 'expected' frequencies as well
'''
m_w_statistic, m_w_pvalue = stat.mannwhitneyu(r1_qual_over_cycle,r2_qual_over_cycle)
k_s_statistic, k_s_pvalue = stat.ks_2samp(r1_qual_over_cycle,r2_qual_over_cycle)

if (m_w_pvalue < 0.05):
    '''
    This may not be the right test, but I couldn't find anything better for now (tried ChiSq and Fishers
    but can't use them as there's more than 2x2 categories
    Also I don't think the data are binned- it is frequencies for each Q score...
    '''
    warnings.warn("Big difference in median quality between read1 and read2")

##Abnormal patterns in data by cycle plot (% bases >Q30)
#
#Generate a data by cycle plot

#Locate the data which contains the quality information only
#first_read_qual_subs
#second_read_qual_subs

cursor.execute(""" SELECT QualByRow.MiSeqRunID,QualByRow.CycleID,
                    OverQ30 AS OverQ30
                    FROM QualByRow 
                    WHERE QualByRow.CycleID = QualByRow.CycleID
                    AND QualByRow.MiSeqRunID = """ + "'" + run_for_import + "'" """
                    GROUP BY QualByRow.MiSeqRunID, QualByRow.CycleID, QualByRow.TileID """)
quality_over_cycle_all = cursor.fetchall()
quality_over_cycle_all_arr = np.asarray(quality_over_cycle_all)
#print(quality_over_cycle_all_arr) #Try to match this data without the need for the extract

x = quality_over_cycle_all_arr[:,1]
y = quality_over_cycle_all_arr[:,2]

pl.figure(10)
f1 = pl.plot(x,y)

#Find the data for the first read
#print(first_read_qual_subs)
#read1_length
#Try to replicate the above plot without the data extract- need proportion of cycle over Q30
#Do an array division number Q30 over total number for each cycle

#Sum each row to get Q30 values
#Read 1
#Need to convert arrays to float arrays or the resultant division will be nearest int (so all 0s)
Q30_by_row_r1 = np.ndarray.astype(np.sum(Q30_r1_arr,axis=1),float)
#Sum each row to get total values
#Need to convert arrays to float arrays or the resultant division will be nearest int (so all 0s)
total_by_row_r1 = np.ndarray.astype(np.sum(first_read_qual_subs,axis=1),float)
proportion_Q30_r1 = np.divide(Q30_by_row_r1,total_by_row_r1)

#Pull out the medians- remember this array is already sorted by cycle
#First chunk the array into slices based on cycle:- start:stop:step
#Test the slicing on the full array that has the cycles included- easier validation that it is working properly
#print(first_read_qual[:(num_tls*num_surfaces):,:]) # This is correct- checked against excel spreadsheet
#print(first_read_qual[:(num_tls*num_surfaces)+1,:]) # Testing that the above does stop where cycle switches from 1 to 2

#Therefore here we have the part without the identifiers for the first read below
#print(first_read_qual_subs[:(num_tls*num_surfaces):,:])
#First thing to do is get the numbers for each quality bin over cycle
#sum this array subset column-wise- this is the number of falling into each quality category, from Q01 to Q50
cycle_qual_binned_vals = np.sum(first_read_qual_subs[:(num_tls*num_surfaces):,:],axis = 0)
#print(cycle_qual_binned_vals)

#Test iterating through the cycles in chunks, cause that is what will need to do
#and then nest the other things within in 

'''
#WORKING HEREs 
lst = []
print(first_read_qual[:,2])
lst.append(first_read_qual[:,2][::(num_tls*num_surfaces)]) # This is correct, but I want the index of this value, not the value
#lst.append(first_read_qual_subs[::(num_tls*num_surfaces),:]) #Test with the one with the cycle info included
print(lst)
'''

'''
for iq,xq in enumerate(first_read_qual[:,2]):
    print(first_read_qual[:,2]) # This is the whole row in which the cycle is stored
    print (first_read_qual[:,2][iq:])
    '''
for iq,xq in enumerate(first_read_qual[:,2][::(num_tls*num_surfaces)]):
    #print(iq)
    #print(iq*(num_tls*num_surfaces))
    #print(num_tls*num_surfaces) #This is 28 (which is 2*14 as expected)
    #print(first_read_qual[(iq*(num_tls*num_surfaces)),2])
    #print(first_read_qual[(iq*(num_tls*num_surfaces)):((iq*(num_tls*num_surfaces))+(num_tls*num_surfaces))]) #Checked and this is the final entry
    quality_chunk = (first_read_qual[(iq*(num_tls*num_surfaces)):((iq*(num_tls*num_surfaces))+(num_tls*num_surfaces))])


'''    
for start in lst:
    print(first_read_qual_subs[start:(num_tls*num_surfaces):,:])
    start += (num_tls*num_surfaces)
    print(np.sum(first_read_qual_subs[start:(num_tls*num_surfaces):,:]))
'''



''' This approach below is too slow
#Multiply each entry by the Q to get the values
quality_vals = np.arange(1,51,1,int)
quality_vals_str = quality_vals.astype(str)
#print(quality_vals_str)
#print(type(quality_vals[0]))
#Do an elementwise multiplication
#Create a list to store the result
bins = []
#print(len(cycle_qual_binned_vals))
#print(len(quality_vals))
#print(np.multiply(cycle_qual_binned_vals_str*quality_vals))
for i,s in enumerate(quality_vals_str):
    bins.append((s*cycle_qual_binned_vals[i]))
print(bins)
'''

#Find the cumulative values on the array subset
cycle_qual_binned_vals_cum = (np.cumsum(cycle_qual_binned_vals))

#The median is at this position
med_rank = (np.sum(cycle_qual_binned_vals)/2.0)

'''
#Testing for an even value of /2
med_rank = 9929106
'''

if(med_rank%1 != 0):
    med_rank = int(med_rank+0.5)
elif(med_rank%1 == 0):
    '''
    This is not a true median as it should be the average of the two values
    med_rank and med_rank+2. However, due to the number of tied values, I don't
    really think it is likely to matter that much.
    '''
    med_rank = (med_rank)

#How to discover which bin this value is in
for cum_ind, cumulative_value in enumerate(cycle_qual_binned_vals_cum):
    if (med_rank < cumulative_value) and (med_rank > (cycle_qual_binned_vals_cum[cum_ind-1])):
        qual_med = cum_ind+1 #As python is 0 indexed

#So the median for cycle 1 of read 1 is 
#print(qual_med)- STOPPED THIS PRINTING OUT FOR NOW WHILE WAS WORKING ON SOMETHING ELSE


'''
print(first_read_qual_subs[::(num_tls*num_surfaces),:])
print(len(first_read_qual_subs[::(num_tls*num_surfaces),:]))
f = (len(first_read_qual_subs[::(num_tls*num_surfaces)]))
'''


#Read 2
Q30_by_row_r2 = np.ndarray.astype(np.sum(Q30_r2_arr,axis=1),float)
total_by_row_r2 = np.ndarray.astype(np.sum(second_read_qual_subs,axis=1),float)
proportion_Q30_r2 = np.divide(Q30_by_row_r2,total_by_row_r2)

#Pull out the medians


'''
pl.figure(11)
f2 = pl.plot(proportion_Q30_r1)

pl.figure(12)
f3 = pl.plot(proportion_Q30_r2)

#Concatenate the arrays to get the same plot as the original data extract to double-check
proportion_Q30_rboth = np.concatenate((proportion_Q30_r1,proportion_Q30_r2))
pl.figure(13)
f4 = pl.plot(proportion_Q30_rboth)

#Do the median plots




pl.show()
'''
#Does it look how one would expect?

