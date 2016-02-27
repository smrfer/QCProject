'''
Created on Jan 29, 2016

@author: Sara
'''
#This file is the one that became the MultiSpreadsheet file, before I did the write out

#Required imports
from __future__ import print_function
import MySQLdb
import sys
import warnings
import numpy as np
import bisect
import scipy
from scipy.optimize import curve_fit
import scipy.stats as stat
import matplotlib.pyplot as pl
import re

#'''
###Write out stdout to a file
#See if can redirect output to a file
file_loc = sys.path[0]
file_name = file_loc + "\\outputs_log.txt"
sys.stdout = open(file_name, 'w')
#'''
#Load in a bunch of runs
#Later on this will trigger from Matt's transfer program

#Connect to the database- user with select privileges only
try:
    db = MySQLdb.connect("localhost",sys.argv[1],sys.argv[2], "ngsqc" ) #Pass username and password as command line arguments

except:
    sys.exit("Enter correct username and password!")

cursor = db.cursor()
    
#Open the list of runs created with GenerateRunList.py
outpath = sys.path[0]
outpath = outpath + "\\runs.txt"
file_of_runs = open(outpath, 'r')

#Import all runs from list of runs generated above- this is currently all of the runs in the database
for run in file_of_runs:
    #print(run) # Keep track of where we are
    run_for_import = run.rstrip() #Trailing newline /n means select otherwise doesn't work
    print(run_for_import) # Keep track of where we are

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
    
    ind_reads = 0
    for read_extract in reads_info_arr_int:  
        if read_extract[2] == 0:
            #Read is not an index read
            if ((read_extract[0]) == 1 ) and (read_extract[1] == reads_info_arr_int[:,1].max()):
                #R1 is the first one
                read1_length = read_extract[1]
            else:
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
    
    if current_run_extracted == None:
        #warnings.warn("There is no InterOp data for this run")
        print("There is no InterOp data for this run")
        #Break out of the loop and go on with the next run
        continue

    sql_command = """ SELECT MAX(CorrectedIntMetrics.CycleID)
                    FROM CorrectedIntMetrics
                    WHERE CorrectedIntMetrics.MiSeqRunID = """ + "'" + run_for_import + "'"
    cursor.execute(sql_command)
    current_run_called = cursor.fetchall()[0][0]

    sql_command = """ SELECT MAX(QualityMetrics.CycleID)
                    FROM QualityMetrics
                    WHERE QualityMetrics.MiSeqRunID = """ + "'" + run_for_import + "'"
    cursor.execute(sql_command)
    current_run_scored = cursor.fetchall()[0][0]
    
    ##Is the run complete
    ##Check that the total number of extracted matches the number of cycles from the reads- if not then there's a problem
    #Remove this for now so that code continues to execute
    ###assert current_run_extracted  == num_cycles_reads
    ##Are the extracted, called and scored numbers equal? i.e. is run analysis complete
    if current_run_extracted != current_run_called == current_run_scored:
        #warnings.warn("Run " + str(run_for_import) + " incomplete")
        print("Run analysis " + str(run_for_import) + " incomplete")
    
    ##Are all the reagents in date from the run date?
    #Extract run date
    cursor.execute(""" SELECT MiSeqRun.RunStartDate
                    FROM MiSeqRun
                    WHERE MiSeqRun.MiSeqRunID = """ + "'" + run_for_import + "'")
    run_date = cursor.fetchall()[0][0]
    
    ##Extract reagent dates
    cursor.execute(""" SELECT MiSeqRun.FlowCellExpiry, MiSeqRun.PR2BottleExpiry, MiSeqRun.ReagentKitExpiry  
                    FROM MiSeqRun
                    WHERE MiSeqRun.MiSeqRunID = """ + "'" + run_for_import + "'")
    reagent_dates = cursor.fetchall()[0]
    for reagent_date in reagent_dates:
        if (reagent_date < run_date):
            #warnings.warn("One of the run reagents or the flow cell was out of date")
            print("One of the run reagents or the flow cell was out of date")
            
    ##Extract version number of reagents
    cursor.execute(""" SELECT MiSeqRun.KitVersionNumber
                    FROM MiSeqRun
                    WHERE MiSeqRun.MiSeqRunID = """ + "'" + run_for_import + "'")
    kit_version = cursor.fetchall()[0][0]
    kt = str(kit_version)

    #Create a dictionary with threshold values for number of reads passing filter
    #Source: http://www.illumina.com/systems/miseq/performance_specifications.html
    threshold_reads = {("2","SE"):(12000000,15000000),("2","PE"):(24000000,30000000),("2","SE"):(22000000,25000000),("3","PE"):(44000000,50000000)}

    #Pull number of reads for entire run
    cursor.execute(""" SELECT SUM(Value) AS ReadsPerRun
                    FROM TileMetrics
                    WHERE TileMetrics.MiSeqRunID = """ + "'" + run_for_import + "'" """
                    AND TileMetrics.CodeID = '102'
                    GROUP BY TileMetrics.MiSeqRunID """)
    reads_per_run = cursor.fetchall()[0][0]
    reads_per_run = (int(reads_per_run))

    #Pull number of reads passing filter
    cursor.execute(""" SELECT SUM(Value) AS ReadsPerRunPF
                    FROM TileMetrics
                    WHERE TileMetrics.MiSeqRunID = """ + "'" + run_for_import + "'" """
                    AND TileMetrics.CodeID = '103'
                    GROUP BY TileMetrics.MiSeqRunID """)
    reads_per_run_pf = cursor.fetchall()[0][0]
    reads_per_run_pf = (int(reads_per_run_pf))

    #Work out proportion of runs 
    proportion_reads_per_run_pf = (float(reads_per_run_pf))/(float(reads_per_run))
    perc_reads_per_run_pf = (100*proportion_reads_per_run_pf)
    read_perc_threshold = 80 #Set the low threshold for reads passing filter

    #Trigger warning if a low proportion/percentage of reads pass filter
    if perc_reads_per_run_pf < read_perc_threshold:
        #warnings.warn("Fewer than 80% of reads passing filter")
        print("Fewer than 80% of reads passing filter")
    
    #Retrieve the values associated with the kit version
    #All runs are with paired end reads!!! ASSUME PAIRED END FOR NOW
    threshold_reads_vals = threshold_reads.get((str(kit_version),"PE"))
    
    if threshold_reads_vals == None:
        #warnings.warn("No threshold read number available for kit version " + kt)
        print("No threshold read number available for kit version " + kt)

    else:
            #warnings.warn("Read count outside Illumina recommended range. Paired end sequencing assumed")
        if (reads_per_run_pf < threshold_reads_vals[0]):
            print("Read count lower than Illumina recommended range at " + str("%.0f" %reads_per_run_pf) + " on a v" + kt + " kit. Paired end sequencing assumed.")
        elif(reads_per_run_pf > threshold_reads_vals[1]):
            print("Read count higher than Illumina recommended range at " + str("%.0f" %reads_per_run_pf) + "on a v" + kt + " kit. Paired end sequencing assumed.")

    #Create a dictionary with threshold cluster densities for reagent version numbers
    #Values outside of these should generate a warning
    #Source https://my.illumina.com/MyIllumina/Bulletin/AH1453j-w0KpvCnZRqLYlA/cluster-density-specifications-for-illumina-sequen
    threshold_dens = {"2":(1000,1200),"3":(1200,1400)}
    #Set an outside value exceeding which generates an error
    outside_threshold_dens = {"2":(850,1250),"3":(1100,1500)}
    
    ##Cluster density
    cursor.execute(""" SELECT TileMetrics.TileID, TileMetrics.Value/1000 AS ClusterDensity
                    FROM TileMetrics
                    WHERE TileMetrics.CodeID = '100'
                    AND TileMetrics.MiSeqRunID = """ + "'" + run_for_import + "'")
    cluster_density_full = cursor.fetchall()
    cluster_density_full_arr = np.array(cluster_density_full)
    mean_dens = (np.mean(cluster_density_full_arr[:,1]))
    max_dens = (np.max(cluster_density_full_arr[:,1]))
    min_dens = (np.min(cluster_density_full_arr[:,1]))
    std_dens = (np.std(cluster_density_full_arr[:,1])) # This default does across axis=0 which is correct
    median_dens = (np.median(cluster_density_full_arr[:,1]))

    ##Cluster density passing filter
    cursor.execute(""" SELECT TileMetrics.TileID, TileMetrics.Value/1000 AS ClusterDensity
                    FROM TileMetrics
                    WHERE TileMetrics.CodeID = '101'
                    AND TileMetrics.MiSeqRunID = """ + "'" + run_for_import + "'")
    cluster_density_full_pf = cursor.fetchall()
    cluster_density_full_pf_arr = np.array(cluster_density_full_pf)
    mean_dens_pf = (np.mean(cluster_density_full_pf_arr[:,1]))
    std_dens_pf = (np.std(cluster_density_full_pf_arr[:,1]))
    median_dens_pf = (np.median(cluster_density_full_pf_arr[:,1]))

    #Retrieve the values associated with the kit version
    threshold_vals_dens = threshold_dens.get(str(kit_version),None)
    outside_threshold_vals_dens = outside_threshold_dens.get(str(kit_version),None)
    
    if threshold_vals_dens == None or outside_threshold_vals_dens == None:
        #warnings.warn("No threshold cluster density available for kit version " + kt)
        print("No threshold cluster density available for kit version " + kt)
    else:
        cluster_d = str("%.2f" %mean_dens_pf)
        #Checks for thresholding levels on cluster density
        if (mean_dens_pf < outside_threshold_vals_dens[0]):
            #raise Exception("Cluster density very low at "+ cluster_d + " on a v" + kt + " kit")
            #Removed exception so that code doesn't stop executing when multiple runs go in
            #warnings.warn("Cluster density very low at "+ cluster_d + " on a v" + kt + " kit")
            print("Cluster density passing filter very low at "+ cluster_d + " on a v" + kt + " kit")
        elif (mean_dens_pf > outside_threshold_vals_dens[1]):
            #raise Exception("Cluster density very high at "+ cluster_d + " on a v" + kt + " kit")
            #Removed exception so that code doesn't stop executing when multiple runs go in
            #warnings.warn("Cluster density very high at "+ cluster_d + " on a v" + kt + " kit")
            print("Cluster density passing filter very high at "+ cluster_d + " on a v" + kt + " kit")
        elif (mean_dens_pf < threshold_vals_dens[0]):
            #outside Illumina recommended thresholds
            #warnings.warn("Cluster density is low at " + cluster_d + " on a v" + kt + " kit")
            print("Cluster density passing filter is low at " + cluster_d + " on a v" + kt + " kit")
        elif (mean_dens_pf > threshold_vals_dens[1]):
            #outside Illumina recommended thresholds
            #warnings.warn("Cluster density is high at " + cluster_d + " on a v" + kt + " kit")
            print("Cluster density passing filter is high at " + cluster_d + " on a v" + kt + " kit")

    #Is there a big range in the cluster density?- this is over tiles and could indicate a problem with a tile
    std_threshold = float(mean_dens)*0.05 #Pick the correct threshold value (gone for 5% of the mean here)- There was not really any need to do this as COV is already normalised
    threshold_COV_cluster_density = 0.05 # (5%)

    #This is all great but why not have a go at the coefficient of variation, which is the standardised measure of dispersion
    COV_cluster_density = std_dens/mean_dens # Proportion of the mean that falls within 1 standard deviation

    if COV_cluster_density > threshold_COV_cluster_density:
        #warnings.warn("Large range in cluster densities. Possible issue with a tile.")
        print("Large range in cluster densities. Possible issue with a tile.")

    #Is there a big gap between cluster density and cluster density passing filter?
    #If they are doing boxplots then it should be based on the median
    perc_diff_med_cd = (median_dens_pf/median_dens*100)
    
    threshold_med_cd = 85 #Is this a useful threshold?
    
    if perc_diff_med_cd < threshold_med_cd:
        #warnings.warn("Low number of clusters passing filter") 
        print("Low number of clusters passing filter. Only " + str("%.2f" %perc_diff_med_cd) + "% passing filter.")    
    
    #Look at reads separately
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
    qual_metrics_arr_mod_int = qual_metrics_arr_mod.astype(np.int64) #Need a longint here or get a buffer overflow later
    #Need to sort the data based on cycle if going to slice it later (3rd column)
    qual_metrics_arr_mod_int_sorted = qual_metrics_arr_mod_int[qual_metrics_arr_mod_int[:,2].argsort()]
    #Remove the three entries that aren't actual quality bins
    qual_metrics_arr_mod_int_sorted_subs = (qual_metrics_arr_mod_int_sorted[:,3:qual_num_cols])

    #Work out the Q30 proportion over the entire array
    Q30_qual_arr = qual_metrics_arr_mod_int_sorted_subs[:,29:len(qual_metrics_arr_mod_int_sorted_subs[0,:])] # 29 is the position of Q30
    Q30_number = (np.sum(Q30_qual_arr))
    Qtotal_number = (np.sum(qual_metrics_arr_mod_int_sorted_subs))
    prop_Q30_qual = (float(Q30_number)/float(Qtotal_number))
    
    #Get the recommended Q30 thresholds and test if run meets the criteria
    #Source: http://www.illumina.com/systems/miseq/performance_specifications.html
    #For Q30 averaged across entire run
    illumina_Q30_threshold_bins = {"2":(25,150,250),"3":(75,300)}
    illumina_Q30_threshold_bins_for_kit = illumina_Q30_threshold_bins.get(str(kit_version),None)

    try:
        cycle_kit = -1
        for threshold in illumina_Q30_threshold_bins_for_kit:
            if (read1_length == threshold) | ((read1_length-1) == threshold):
                cycle_kit = threshold

        if (cycle_kit == -1):
            ind_of_next_higher = bisect.bisect(illumina_Q30_threshold_bins_for_kit, read1_length)
            if ind_of_next_higher > (len(illumina_Q30_threshold_bins_for_kit)-1): #handle case where number is higher than last one in tuple. -1 as python 0 indexed.
                cycle_kit = illumina_Q30_threshold_bins_for_kit[(ind_of_next_higher-1)]
            else:
                cycle_kit = illumina_Q30_threshold_bins_for_kit[ind_of_next_higher]
        illumina_Q30_thresholds = {("2","25"):(0.90),("2","150"):(0.80),("2","250"):(0.75),("3","75"):(0.85),("3","300"):(0.70)}
        Q30_illumina_threshold = illumina_Q30_thresholds.get((str(kit_version),str(cycle_kit)),None)
    
    #Now handle the cases where there's no kit
    except TypeError:
        print("No Q30 threshold available for kit version " + str(kt) + ". Q30 threshold set to 85%") # Set a fallback value for if threshold value not in dictionary
        Q30_illumina_threshold = 0.85
    
    if prop_Q30_qual < Q30_illumina_threshold:
        #warnings.warn("Fewer than 90% of bases are over Q30")
        print("Number of bases over Q30 failed to meet Illumina recommended thresholds")
        print("Only " + str("%.0f" %(prop_Q30_qual*100)) + "% of bases over Q30")

    ##To split into separate reads based on number of cycles
    ##There is a cycle per each tile, which includes top and bottom surface (so 2*number of tiles)
    ##Obtain the number of tiles
    cursor.execute(""" SELECT MiSeqRun.NumTiles
                    FROM MiSeqRun
                    WHERE MiSeqRunID = """ + "'" + run_for_import + "'")
    num_tls = cursor.fetchall()[0][0]
    
    #Obtain the number of surfaces
    cursor.execute(""" SELECT MiSeqRun.NumSurfaces
                    FROM MiSeqRun
                    WHERE MiSeqRunID = """ + "'" + run_for_import + "'")
    num_surfaces = cursor.fetchall()[0][0]

    #How the reads (without the index reads) extend
    r1_end = num_surfaces*num_tls*read1_length
    #read1
    first_read_qual = qual_metrics_arr_mod_int_sorted[0:r1_end,:]
    #read2
    r2_start = r1_end + (ind_reads*num_surfaces*num_tls)
    second_read_qual = qual_metrics_arr_mod_int_sorted[r2_start:qual_num_rows,:]

    #Subset of array containing bins Q01-Q50 only- start from position 3 as started from the int array so
    #MiSeqRunID has already been removed- this slicing has been tested to slice at the correct position
    first_read_qual_subs =(first_read_qual[:,3:qual_num_cols])
    second_read_qual_subs =(second_read_qual[:,3:qual_num_cols])

    #Find the proportion of Q30 for the first read
    Q30_r1_arr = first_read_qual_subs[:,29:len(first_read_qual_subs[0,:])]
    Q30_r1 = (np.sum(Q30_r1_arr))
    Qtotal_r1 = (np.sum(first_read_qual_subs))
    prop_Q30_r1 = (float(Q30_r1)/float(Qtotal_r1))

    #Find the proportion of Q30 for the second read
    if r2_start < (len(qual_metrics_arr_mod_int_sorted)):
        #Handle the case where there is no second read
        Q30_r2_arr = second_read_qual_subs[:,29:len(second_read_qual_subs[0,:])]
        Q30_r2 = (np.sum(Q30_r2_arr))
        Qtotal_r2 = (np.sum(second_read_qual_subs))
        prop_Q30_r2 = (float(Q30_r2)/float(Qtotal_r2))
        
    #Is there a big difference in >Q30 between r1 and r2?- Test for significance
    #Just look to see if there is a difference in the spread of quality scores perhaps
    #For this will need to create a 1D distribution across the range of quality scores
    #We already have this with the first/second_read_qual_subs- just need to sum it over the correct axis
    r1_qual_distn = np.sum(first_read_qual_subs,axis=0)
    r2_qual_distn = np.sum(second_read_qual_subs,axis=0)

    #Non-parametric, so use rank sum test (Wilcoxon?)
    #Need to figure out a useful test for this kind of frequency data
    '''
    K-S is more sensitive to changes in shape of distribution etc. 
    '''
    #K-S downsampling to try to avoid out of memory error
    r1_qual_distn_downsample = (np.divide(r1_qual_distn,1000))
    r2_qual_distn_downsample = (np.divide(r2_qual_distn,1000))
    '''
    #Can't put count data into this- need to change it if use- other way was too sensitive- use count data
    k_s_statistic, k_s_pvalue = stat.ks_2samp(r1_qual_distn,r2_qual_distn) # Can't do this as only for continuous email
    '''
    #Downsampled data to avoid out of memory error
    k_s_statistic, k_s_pvalue = stat.ks_2samp(r1_qual_distn_downsample,r2_qual_distn_downsample)   
    #print(k_s_pvalue)
    
    if (k_s_pvalue < 0.05): # 95% confidence, was at 0.05
        '''
        This may not be the right test, but I couldn't find anything better for now (tried ChiSq and Fishers
        but can't use them as there's more than 2x2 categories
        Also I don't think the data are binned- it is frequencies for each Q score...
        '''
        #warnings.warn("Big difference in median quality between read1 and read2") # Was a median, but mann whitney tie correction broken in scipy
        print("Big difference in quality between read 1 and read 2")

    ##Abnormal patterns in data by cycle plot (% bases >Q30)?
    #Sum each row to get Q30 values
    #Read 1
    #Need to convert arrays to float arrays or the resultant division will be nearest int (so all 0s)
    Q30_by_row_r1 = np.ndarray.astype(np.sum(Q30_r1_arr,axis=1),float)

    #Sum each row to get total values
    #Need to convert arrays to float arrays or the resultant division will be nearest int (so all 0s)
    total_by_row_r1 = np.ndarray.astype(np.sum(first_read_qual_subs,axis=1),float)
    proportion_Q30_r1 = np.divide(Q30_by_row_r1,total_by_row_r1)
    proportion_Q30_r1 = np.nan_to_num(proportion_Q30_r1)

    #Tested using first_read_qual so that I could see the cycle numbers, now swapped over to first_read_qual_subs
    r1_qual_med = []
    Q30_median_over_cycle_r1 = []
    for qual_i,qual in enumerate(first_read_qual_subs[:,2][::(num_tls*num_surfaces)]):
        quality_chunk = (first_read_qual_subs[(qual_i*(num_tls*num_surfaces)):((qual_i*(num_tls*num_surfaces))+(num_tls*num_surfaces))])

        cycle_qual_binned_vals = np.sum(quality_chunk,axis = 0) #Checked is correct for first cycle
    
        #Find the cumulative values on the array subset
        cycle_qual_binned_vals_cum = (np.cumsum(cycle_qual_binned_vals))

        #The median is at this position
        med_rank = (np.sum(cycle_qual_binned_vals)/2.0)
    
        #Proportion of total with this Q value
        quality_percentage = ((cycle_qual_binned_vals*100)/(float(np.sum(cycle_qual_binned_vals))))

        #Low down qualities with high percentages
        '''
        From the colour coding on the Illumina SAV, I think we will be looking at 15% and over in any
        bin <Q30
        '''
        #Set quality threshold for appearance in heatmap to 15
        qual_perc_o15 = np.where(quality_percentage > 15)
        #The Q score is ans+1 in this case as python is 0-indexed
        qual_perc_o15_under_Q30 = np.where(qual_perc_o15[0] < 29)
        if qual_perc_o15_under_Q30[0].size > 0:
            print("High percentage of total clusters under Q30 for cycle " + str(qual_i+1))

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
    
        r1_qual_med.append(qual_med) 
        Q30_proportion_chunk = (proportion_Q30_r1[(qual_i*(num_tls*num_surfaces)):((qual_i*(num_tls*num_surfaces))+(num_tls*num_surfaces))])
        Q30_median_over_cycle_r1.append((np.median(Q30_proportion_chunk)))

    r1_qual_med = np.asarray(r1_qual_med)
    Q30_median_over_cycle_r1 = np.asarray(Q30_median_over_cycle_r1)

    #Work out the degradation coefficient for the loss in quality over the read
    Q30_median_over_cycle_r1_xdata = (np.arange(1,(len(Q30_median_over_cycle_r1)+1))) # Want it to start at 1 and stop at 101

    #function to fit- make it linear
    #Initial guesses for parameters
    p1 = 0.5
    p2 = 0.5

    def func(x, p1,p2):
        return(p1 * x + p2) #Linear
    
    #This requires a function as input
    optimal_vals_Q30_r1, covar_Q30_r1 = curve_fit(func,Q30_median_over_cycle_r1_xdata,Q30_median_over_cycle_r1, p0=(p1,p2))
    linear_pred_r1 = (optimal_vals_Q30_r1[0] * Q30_median_over_cycle_r1_xdata + optimal_vals_Q30_r1[1])
    #Set variable to the slope of the line
    slope_Q30_r1 = optimal_vals_Q30_r1[0]

    if abs(slope_Q30_r1) > 0.0005:
        #warnings.warn("Big drop in quality towards the end of read 1")
        print("Big drop in quality towards the end of read 1")

    #Read 2
    if r2_start < (len(qual_metrics_arr_mod_int_sorted)):
        #Handle the case where there is no second read
        Q30_by_row_r2 = np.ndarray.astype(np.sum(Q30_r2_arr,axis=1),float)
        total_by_row_r2 = np.ndarray.astype(np.sum(second_read_qual_subs,axis=1),float)
        proportion_Q30_r2 = np.divide(Q30_by_row_r2,total_by_row_r2)
        proportion_Q30_r2 = np.nan_to_num(proportion_Q30_r2)

        #Pull out the medians
        r2_qual_med = []
        Q30_median_over_cycle_r2 = []
        for qual_i,qual in enumerate(second_read_qual_subs[:,2][::(num_tls*num_surfaces)]):
            quality_chunk = (second_read_qual_subs[(qual_i*(num_tls*num_surfaces)):((qual_i*(num_tls*num_surfaces))+(num_tls*num_surfaces))])
            cycle_qual_binned_vals = np.sum(quality_chunk,axis = 0) #Checked is correct for first cycle  
            #Find the cumulative values on the array subset
            cycle_qual_binned_vals_cum = (np.cumsum(cycle_qual_binned_vals))
            #The median is at this position
            med_rank = (np.sum(cycle_qual_binned_vals)/2.0)
            quality_percentage = ((cycle_qual_binned_vals*100)/(float(np.sum(cycle_qual_binned_vals))))

            '''
            From the colour coding on the Illumina SAV, I think we will be looking at 15% and over in any
            bin <Q30
            '''    
            qual_perc_o15 = np.where(quality_percentage > 15)
            #The Q score is ans+1 in this case as python is 0-indexed
            qual_perc_o15_under_Q30 = np.where(qual_perc_o15[0] < 29)
            if qual_perc_o15_under_Q30[0].size > 0:
                #As this is r2 need to add on read 1 and the index reads to get the cycle number- checked for correct length
                print("High percentage of total clusters under Q30 for cycle " + str((qual_i+1)+read1_length+ind_reads))

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
    
            r2_qual_med.append(qual_med) 
            Q30_proportion_chunk = (proportion_Q30_r2[(qual_i*(num_tls*num_surfaces)):((qual_i*(num_tls*num_surfaces))+(num_tls*num_surfaces))])
            Q30_median_over_cycle_r2.append((np.median(Q30_proportion_chunk)))

        r2_qual_med = np.asarray(r2_qual_med)
        Q30_median_over_cycle_r2 = np.asarray(Q30_median_over_cycle_r2)

        #Work out the degradation coefficient for the loss in quality over the read
        Q30_median_over_cycle_r2_xdata = (np.arange(1,(len(Q30_median_over_cycle_r2)+1))) # Want it to start at 1 and stop at 101
        #Initial guesses for parameters- already above for r1, function also already defined above
        #This requires a function as input
        optimal_vals_Q30_r2, covar_Q30_r2 = curve_fit(func,Q30_median_over_cycle_r2_xdata,Q30_median_over_cycle_r2, p0=(p1,p2))
        linear_pred_r2 = (optimal_vals_Q30_r2[0] * Q30_median_over_cycle_r2_xdata + optimal_vals_Q30_r2[1])

        #Set variable to the slope of the line
        slope_Q30_r2 = optimal_vals_Q30_r2[0]

        if abs(slope_Q30_r2) > 0.0005:
            #warnings.warn("Big drop in quality towards the end of read 2")
            print("Big drop in quality towards the end of read 2")

    #Indexing- different proportion of reads?
    cursor.execute(""" SELECT * FROM IndexMetricsMSR
                    WHERE IndexMetricsMSR.MiSeqRunID = """ + "'" + run_for_import + "'" """
                    ORDER By IndexMetricsMSR.IndexName """)
    index_metrics = cursor.fetchall() #[0][0]
    index_metrics_arr = np.asarray(index_metrics)  
    
    if len(index_metrics_arr) == 0:
        #warnings.warn("No index information for run " + str(run_for_import))
        print("No index information for run " + str(run_for_import))
        continue #Continue with the next interation of the loop 
    
    #Note that this is sorted by Index Name and therefore chunks of 28 (as before with the quality by cycle)
    total_per_index = []
    for inde_i,inde in enumerate(index_metrics_arr[:,5][::(num_tls*num_surfaces)]):
        index_chunk = (index_metrics_arr[:,5][(inde_i*(num_tls*num_surfaces)):((inde_i*(num_tls*num_surfaces))+(num_tls*num_surfaces))])
        index_chunk_int = np.ndarray.astype(index_chunk,int)
        total_per_index.append(np.sum(index_chunk_int))

    #Obtain the total number of counts per sample (over all tiles) and then this as a proportion of total number
    #passing filter (which includes undetermined reads)
    total_per_index_arr = np.asarray(total_per_index)
    prop_pf_per_index_arr = ((total_per_index_arr)/(float(reads_per_run_pf)*100)) # Integer division gives 0
    
    #Either/Or for labelling
    sample_names = index_metrics_arr[:,6][::(num_tls*num_surfaces)]  
    #Set the index names to the sequence of the indices
    #index_sequence_names = index_metrics_arr[:,4][::(num_tls*num_surfaces)]  
    #Set the index names to the name of the sample
    index_names = sample_names

    index_x_axis = np.arange(len(index_names)) #This is required for the later setting of xticks to labels

    ##Before deciding on the outlying samples, the NTC should be removed as it is a special case
    #It would still be good if it appeared on the plot though- this has been achieved
    location_of_ntc = []
    for samp_ind,samp in enumerate(sample_names):
        if re.search("ntc", samp, re.IGNORECASE):
            '''
            Find the NTC and remove it from the list of outlying samples, leaving only the samples
            which are over or under represented
            This version assumed that there was one NTC, amended to handle the case where there
            is more than one
            '''
            location_of_ntc.append(samp_ind)

    #Create an array containing the NTC entries only
    prop_pf_index_ntc_arr = prop_pf_per_index_arr[location_of_ntc]
    sample_names_ntc = sample_names[location_of_ntc]
    ntc_arr = np.vstack((sample_names_ntc,prop_pf_index_ntc_arr)).T
        
    #Create an array containing all the entries except the NTC ones        
    prop_pf_index_subs_arr = np.delete(prop_pf_per_index_arr,location_of_ntc)
    sample_names_subs = np.delete(sample_names,location_of_ntc)
    not_ntc_arr = np.vstack((sample_names_subs,prop_pf_index_subs_arr)).T

    ind_mean = (np.mean(prop_pf_index_subs_arr))
    ind_std = (np.std(prop_pf_index_subs_arr))
    ind_high_threshold = (ind_mean + (2*ind_std))
    ind_low_threshold = (ind_mean - (2*ind_std))

    outlying_indexes = (np.where((prop_pf_index_subs_arr < ind_low_threshold) | (prop_pf_index_subs_arr > ind_high_threshold)))
    outlying_sample_indexes = (sample_names_subs[outlying_indexes[0]])
    outlying_samples_values_arr = np.vstack((outlying_sample_indexes,prop_pf_index_subs_arr[outlying_indexes[0]])).T

    #Coefficient of variation
    index_COV = (ind_std/ind_mean)
    threshold_index_COV = 0.03 # Set to 3% otherwise very low samples won't trigger this (known because of COV value including NTC below)
                                # This is way too sensitive at the moment (Matt suggests 5%)

    if index_COV > threshold_index_COV:
        #warnings.warn("Big range over different sample indices") # Note that NTCs are excluded by this code
        print("Big range over different sample indices")

    if (len(outlying_indexes[0])) > 0:
        '''
        NEED TO WORK ON HOW TO PRESENT THIS DATA TO THE USER!! Also this is slightly redundant with the COV- but threshold is at 5% there, so this is more sensitive
        '''
        #warnings.warn("There is at least one outlying sample")
        print("There is at least one outlying sample")
        low_num_reads_ind = (np.where(outlying_samples_values_arr[:,1] < ind_low_threshold))[0]
        low_num_reads = (outlying_samples_values_arr[low_num_reads_ind,:])
        high_num_reads_ind = (np.where(outlying_samples_values_arr[:,1] > ind_high_threshold))[0]
        high_num_reads = (outlying_samples_values_arr[high_num_reads_ind,:])

    #Is the NTC elevated above baseline (i.e. is there contamination in the run?)
    NTC_threshold = 1.0
    NTC_threshold = 0.3
    print(prop_pf_index_ntc_arr)
    
    if (len(np.where(prop_pf_index_ntc_arr > NTC_threshold)[0])) > 0: #If there is an entry in the array of the where
        #warnings.warn("NTC has a higher than expected proportion of reads")
        print("NTC has a higher than expected proportion of reads")


