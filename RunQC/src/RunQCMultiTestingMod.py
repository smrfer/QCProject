'''
Created on 24 Jan 2016

@author: Admin
'''
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
from numpy import nan

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
    #run_for_import = '160104_M02641_0062_000000000-AL603' #This is a test
    #run_for_import = '130405_M00766_0006_000000000-A3FNU' #This is a test
    #run_for_import = '130708_M00766_0023_000000000-A20R8' #This is a test
    #run_for_import = '140314_M00766_0027_000000000-A7C5E' #This is a test
    #run_for_import = '130206_M00766_0002_000000000-A23JM' #This is a test
    #run_for_import =  '130510_M00766_0014_000000000-A3PFJ' #This is a test
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

    for read_extract in reads_info_arr_int:  
        #print(read_extract)
        if read_extract[2] == 0:
            #Read is not an index read
            #print(read_extract[1])
            if ((read_extract[0]) == 1 ) and (read_extract[1] == reads_info_arr_int[:,1].max()):
                #R1 is the first one
                read1_length = read_extract[1]
                #print("read 1 is " + str(read1_length))
            else:
                #R2 is the last one
                read2_length = read_extract[1]
                #print("read 2 is " + str(read2_length))
        elif read_extract[2] == 1:
            ind_reads += read_extract[1]
            #print("index is " + str(ind_reads))
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
    #print("Extracted")
    #print(current_run_extracted)
    
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
    #print("Called")
    #print(current_run_called)

    sql_command = """ SELECT MAX(QualityMetrics.CycleID)
                    FROM QualityMetrics
                    WHERE QualityMetrics.MiSeqRunID = """ + "'" + run_for_import + "'"
    cursor.execute(sql_command)
    current_run_scored = cursor.fetchall()[0][0]
    #print("Scored")
    #print(current_run_scored)

    #Tests to ensure that the wrong bit will trigger- do one at a time
    #current_run_extracted = 2 #Pass test
    #current_run_called = 2 #Pass test
    #current_run_scored = 2 #Pass test

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
    #print(run_date)
    
    ##Extract reagent dates
    cursor.execute(""" SELECT MiSeqRun.FlowCellExpiry, MiSeqRun.PR2BottleExpiry, MiSeqRun.ReagentKitExpiry  
                    FROM MiSeqRun
                    WHERE MiSeqRun.MiSeqRunID = """ + "'" + run_for_import + "'")
    reagent_dates = cursor.fetchall()[0]
    #print(reagent_dates)
    for reagent_date in reagent_dates:
        #print(reagent_date)
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
    #print(threshold_reads)

    #Pull number of reads for entire run
    cursor.execute(""" SELECT SUM(Value) AS ReadsPerRun
                    FROM TileMetrics
                    WHERE TileMetrics.MiSeqRunID = """ + "'" + run_for_import + "'" """
                    AND TileMetrics.CodeID = '102'
                    GROUP BY TileMetrics.MiSeqRunID """)
    #reads_per_run = cursor.fetchall()
    reads_per_run = cursor.fetchall()[0][0]
    #print(reads_per_run)
    reads_per_run = (int(reads_per_run))

    #Pull number of reads passing filter
    cursor.execute(""" SELECT SUM(Value) AS ReadsPerRunPF
                    FROM TileMetrics
                    WHERE TileMetrics.MiSeqRunID = """ + "'" + run_for_import + "'" """
                    AND TileMetrics.CodeID = '103'
                    GROUP BY TileMetrics.MiSeqRunID """)
    reads_per_run_pf = cursor.fetchall()[0][0]
    reads_per_run_pf = (int(reads_per_run_pf))
    #print(reads_per_run_pf)

    #Work out proportion of runs 
    proportion_reads_per_run_pf = (float(reads_per_run_pf))/(float(reads_per_run))
    #print(proportion_reads_per_run_pf)
    perc_reads_per_run_pf = (100*proportion_reads_per_run_pf)
    read_perc_threshold = 80 #Set the low threshold for reads passing filter

    #print(reads_per_run_pf)
    #print(reads_per_run)
    #print(perc_reads_per_run_pf)
    #Trigger warning if a low proportion/percentage of reads pass filter
    if perc_reads_per_run_pf < read_perc_threshold:
        #warnings.warn("Fewer than 80% of reads passing filter")
        print("Fewer than 80% of reads passing filter")
    
    #Retrieve the values associated with the kit version
    #All runs are with paired end reads!!! ASSUME PAIRED END FOR NOW
    #print(kit_version)
    threshold_reads_vals = threshold_reads.get((str(kit_version),"PE"))
    
    if threshold_reads_vals == None:
        #warnings.warn("No threshold read number available for kit version " + kt)
        print("No threshold read number available for kit version " + kt)
        #print(threshold_reads_vals)

        '''
        #Testing
        #reads_per_run_pf = 50
        reads_per_run_pf = 25000000
        #reads_per_run_pf = 50000000
        '''
    else:
        #if (reads_per_run_pf < threshold_reads_vals[0]) | (reads_per_run_pf > threshold_reads_vals[1]):
            #warnings.warn("Read count outside Illumina recommended range. Paired end sequencing assumed")
            #print("Read count outside Illumina recommended range. Paired end sequencing assumed.")
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
    #print("Cluster Density Data Full Extracted")
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
    #print("Cluster Density Data Full Passing Filter Extracted")
    mean_dens_pf = (np.mean(cluster_density_full_pf_arr[:,1]))
    std_dens_pf = (np.std(cluster_density_full_pf_arr[:,1]))
    median_dens_pf = (np.median(cluster_density_full_pf_arr[:,1]))

    #Retrieve the values associated with the kit version
    threshold_vals_dens = threshold_dens.get(str(kit_version),None)
    outside_threshold_vals_dens = outside_threshold_dens.get(str(kit_version),None)
    
    #threshold_vals_dens = 10000 #Test triggering of below if clause with the 'or'
    
    if threshold_vals_dens == None or outside_threshold_vals_dens == None:
        #warnings.warn("No threshold cluster density available for kit version " + kt)
        print("No threshold cluster density available for kit version " + kt)
        #print(threshold_vals_dens)
        #print(outside_threshold_vals_dens)
        '''
        #Testing values
        #mean_dens_pf = 750
        #mean_dens_pf = 650
        #mean_dens_pf = 1000
        #mean_dens_pf = 1200
        '''
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
    #To use std dev or iqr? Start with std dev
    #Threshold for standard deviation
    #print((std_dens/mean_dens)*100) # This is the % of the mean that falls within 1 standard deviation
    #What is a high amount of % of the mean to fall outside of 1sd?
    #Set std threshold to that
    std_threshold = float(mean_dens)*0.05 #Pick the correct threshold value (gone for 5% of the mean here)- There was not really any need to do this as COV is already normalised
    threshold_COV_cluster_density = 0.05 # (5%)
    #print(mean_dens)
    #print(float(mean_dens))
    #print((std_dens/mean_dens))
    #print(float(mean_dens)*0.018159995802775248)
    #print(float(mean_dens)*0.05)
    #print(std_dens)

    #This is all great but why not have a go at the coefficient of variation, which is the standardised measure of dispersion
    COV_cluster_density = std_dens/mean_dens # Proportion of the mean that falls within 1 standard deviation
    #print(COV_cluster_density)
    #print(((std_dens/mean_dens)*100))
    #print(std_threshold)
    '''
    if ((std_dens/mean_dens)*100) > std_threshold: 
        print("Large range in cluster densities. Possible issue with a tile.")
    '''
    if COV_cluster_density > threshold_COV_cluster_density:
        #warnings.warn("Large range in cluster densities. Possible issue with a tile.")
        print("Large range in cluster densities. Possible issue with a tile.")

    #Is there a big gap between cluster density and cluster density passing filter?
    #If they are doing boxplots then it should be based on the median
    perc_diff_med_cd = (median_dens_pf/median_dens*100)
    #Working out a useful threshold- where would median be if was at a value of 'x'- here 85
    #print((float(85)/float(100))*float(median_dens))
    
    threshold_med_cd = 85 #Is this a useful threshold?
    
    if perc_diff_med_cd < threshold_med_cd:
        #warnings.warn("Low number of clusters passing filter") 
        print("Low number of clusters passing filter. Only " + str("%.2f" %perc_diff_med_cd) + "% passing filter.")    
    
    #Large range in cluster densities over different cycles
    #I DO NOT HAVE ACCESS TO THIS DATA- Only have tilewise information and nothing regarding cycle

    '''
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
    print(qual_over_Q30)
    '''
    '''
    #Testing
    qual_over_Q30 = 0.88
    qual_over_Q30 = 0.78
    '''
    '''
    if qual_over_Q30 < 0.85:
        raise Exception("Only " + str("%.0f" %(qual_over_Q30*100)) + "% of bases over Q30")
    elif qual_over_Q30 < 0.90:
        warnings.warn("Fewer than 90% of bases are over Q30")
    '''
    #This could be a plot of number of reads valued at each quality bin
    #Currently would require a separate data extract as the variable stores only the total proportion
    #See below where have all the quality metrics
    
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
    #print(qual_metrics_arr_mod_int)

    #Need to sort the data based on cycle if going to slice it later (3rd column)
    qual_metrics_arr_mod_int_sorted = qual_metrics_arr_mod_int[qual_metrics_arr_mod_int[:,2].argsort()]
    #print(qual_metrics_arr_mod_int_sorted)

    # Remove the three entries that aren't actual quality bins
    qual_metrics_arr_mod_int_sorted_subs = (qual_metrics_arr_mod_int_sorted[:,3:qual_num_cols])
    #print(qual_metrics_arr_mod_int_sorted_subs)
    #print(sum(qual_metrics_arr_mod_int_sorted_subs))
    #print(np.cumsum(sum(qual_metrics_arr_mod_int_sorted_subs)))

    #Work out the Q30 proportion over the entire array
    Q30_qual_arr = qual_metrics_arr_mod_int_sorted_subs[:,29:len(qual_metrics_arr_mod_int_sorted_subs[0,:])] # 29 is the position of Q30
    Q30_number = (np.sum(Q30_qual_arr))
    #print(Q30_number) #This is correct- checked against Excel spreadsheet
    Qtotal_number = (np.sum(qual_metrics_arr_mod_int_sorted_subs))
    #print(Qtotal_number) #This is correct- checked against Excel spreadsheet
    prop_Q30_qual = (float(Q30_number)/float(Qtotal_number))

    #print(prop_Q30_qual)
    #prop_Q30_qual = 0.755475737227 #Testing
    
    #Get the recommended Q30 thresholds and test if run meets the criteria
    #Source: http://www.illumina.com/systems/miseq/performance_specifications.html
    #For Q30 averaged across entire run
    #Logic is a bit awkward, but it works- revisit later to tidy up
    illumina_Q30_threshold_bins = {"2":(25,150,250),"3":(75,300)}
    illumina_Q30_threshold_bins_for_kit = illumina_Q30_threshold_bins.get(str(kit_version),None)
                                                                          
    #print(illumina_Q30_threshold_bins_for_kit)
    #print(type(read1_length))
    
    #read1_length = 156 #This is a test
    #read1_length = 300
    #read1_length = 10
    #read1_length = 150
    #read1_length = 149    
    try:
        cycle_kit = -1
        for threshold in illumina_Q30_threshold_bins_for_kit:
            if (read1_length == threshold) | ((read1_length-1) == threshold):
                #print("go") #check for triggering
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

    #print(Q30_qual_arr)
    #print(qual_metrics_arr_mod_int_sorted_subs)

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
    #print(num_surfaces)    
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
    r1_end = num_surfaces*num_tls*read1_length
    #read1
    first_read_qual = qual_metrics_arr_mod_int_sorted[0:r1_end,:]
    #read2
    r2_start = r1_end + (ind_reads*num_surfaces*num_tls)
    #print(ind_reads)
    second_read_qual = qual_metrics_arr_mod_int_sorted[r2_start:qual_num_rows,:]
    #print(second_read_qual)

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
    #print(prop_Q30_r1*100)

    #Find the proportion of Q30 for the second read
    if r2_start < (len(qual_metrics_arr_mod_int_sorted)):
        #Handle the case where there is no second read
        Q30_r2_arr = second_read_qual_subs[:,29:len(second_read_qual_subs[0,:])]
        Q30_r2 = (np.sum(Q30_r2_arr))
        #print(Q30_r1) #This is correct checked against Excel spreadsheet
        Qtotal_r2 = (np.sum(second_read_qual_subs))
        #print(Qtotal_r1) #This is correct checked against Excel spreadsheet
        prop_Q30_r2 = (float(Q30_r2)/float(Qtotal_r2))
        #print(prop_Q30_r2*100)

    #Is there a big difference in >Q30 between r1 and r2?- Test for significance- this is later, first test spread of quality scores
    #Just look to see if there is a difference in the spread of quality scores perhaps
    #For this will need to create a 1D distribution across the range of quality scores
    #We already have this with the first/second_read_qual_subs- just need to sum it over the correct axis
    r1_qual_distn = np.sum(first_read_qual_subs,axis=0)
    r2_qual_distn = np.sum(second_read_qual_subs,axis=0)

    #Non-parametric, so use rank sum test (Wilcoxon?)
    #Need to figure out a useful test for this kind of frequency data
    '''
    Use Mann Whitney for independent samples? Alternative is Kolmogorov-Smirnov.
    Mann Whitney test deals better with ties (values that are the same and need to be converted into rank)
    We have got a fair bit of tied data (all 0 values and huge numbers of values in same Q bin), so I prefer Mann-Whitney to K-S.
    K-S is more sensitive to changes in shape of distribution etc though.
    Have tried Chi-Sq and Fisher's exact test, but they can't be used because there's more than 2x2 (Fisher) and
    The ChiSq test cannot be used because of the 0s in the 'expected' frequencies as well
    '''
    '''
    #First unpack the data to its non-binned form
    qual_range = np.arange(1,51) #Known a priori that the range of quality values is Q1 to Q50
    '''
    #Unpack the data to its non-binned form
    qual_range = np.arange(1,51) #Known a priori that the range of quality values is Q1 to Q50
    
    #print(np.cumsum(r1_qual_distn)) # Check numbers match with the length of the unpacked array
    #r1_qual_raw = np.repeat(qual_range,r1_qual_distn)# This takes too much memory
    #r2_qual_raw = np.repeat(qual_range,r2_qual_distn)# This takes too much memory
    
    #K-S downsampling to try to avoid out of memory error
    r1_qual_distn_downsample = (np.divide(r1_qual_distn,1000))
    r2_qual_distn_downsample = (np.divide(r2_qual_distn,1000))
    
    '''
    pl.plot(r1_qual_distn_downsample)
    pl.plot(r2_qual_distn_downsample)
    pl.show()
    '''
       
    #'''THE QUAL RAW DONWSAMPLE DEFINITELY WANTS A 'DISCRETE' TEST OF SOME SORT
    r1_qual_raw_downsample = np.repeat(qual_range,(r1_qual_distn_downsample/1000)) # Not being used atm- have temp /1000 again 23/02
    r2_qual_raw_downsample = np.repeat(qual_range,(r2_qual_distn_downsample/1000)) # Not being used atm- have temp /1000 again 23/02
    
    k_s_statistic, k_s_pvalue = stat.ks_2samp(r1_qual_raw_downsample,r2_qual_raw_downsample)
    print(k_s_pvalue)
    #'''
    
    '''
    pl.plot(r1_qual_raw_downsample)
    pl.plot(r2_qual_raw_downsample)
    pl.show()
    '''
    
    '''
    m_w_statistic, m_w_pvalue = stat.mannwhitneyu(r1_qual_raw_downsample,r2_qual_raw_downsample)
    print(m_w_pvalue)
    '''
    
    '''
    print(r1_qual_raw_downsample)
    print(r2_qual_raw_downsample)
    #print(np.cumsum(r1_qual_distn))
    #print(np.sum(r1_qual_raw_downsample))
    '''
    #Create bins of quality data
    '''
    print(r1_qual_distn)
    print(r1_qual_distn[0:25])
    print(r1_qual_distn[25:49])
    print(np.sum(r1_qual_distn[0:25]))
    print(np.sum(r1_qual_distn[25:49]))
    print(np.sum(r1_qual_distn))
    '''
    '''
    r1_qual_bin_1 = np.sum(r1_qual_distn[0:25])
    r1_qual_bin_2 = np.sum(r1_qual_distn[25:49])
    r2_qual_bin_1 = np.sum(r2_qual_distn[0:25])
    r2_qual_bin_2 = np.sum(r2_qual_distn[25:49])
    
    r1_qual_chi = np.asarray((r1_qual_bin_1,r1_qual_bin_2))
    r2_qual_chi = np.asarray((r2_qual_bin_1,r2_qual_bin_2))
    
    print(r1_qual_chi)
    print(r2_qual_chi)
    
    chi, chi_p_value = stat.chisquare(r2_qual_chi,f_exp=r1_qual_chi)
    g, g_p_value = stat.power_divergence(r2_qual_chi,r1_qual_chi)
    
    print(chi_p_value)
    print(chi)
    
    print(g_p_value)
    '''
    '''
    #Can't put count data into this- need to change it if use
    k_s_statistic, k_s_pvalue = stat.ks_2samp(r1_qual_distn,r2_qual_distn) # Can't do this as only for continuous email
    '''
    #Downsampled data to avoid out of memory error
    #k_s_statistic, k_s_pvalue = stat.ks_2samp(r1_qual_raw_downsample,r2_qual_raw_downsample)
    #k_s_statistic, k_s_pvalue = stat.ks_2samp(r1_qual_raw_downsample,r2_qual_raw_downsample)
    #m_w_statistic, m_w_pvalue = stat.mannwhitneyu(r1_qual_raw_downsample,r2_qual_raw_downsample) #Never going to work because of bug
    #t_statistic, t_pvalue = stat.ttest_ind(r1_qual_raw_downsample,r2_qual_raw_downsample)
    #t_statistic, t_pvalue = stat.ttest_ind(r1_qual_raw_downsample,r1_qual_raw_downsample)
    
    k_s_statistic, k_s_pvalue = stat.ks_2samp(r1_qual_distn_downsample,r2_qual_distn_downsample)
    
    #print(r1_qual_distn)
    #print(r1_qual_distn.transpose())
    #chi2, chi_pvalue = stat.chisquare(r1_qual_distn,r2_qual_distn) #No
    #fish, fish_pvalue =
    #gtest, gtest_pvalue = (r1_qual_distn,r2_qual_distn,lambda_="log-likelihood") 
    #print(gtest_pvalue) 
    #print(fish_pvalue)
    #print(np.mean(r1_qual_raw))
    #print(np.mean(r2_qual_raw))
    #print(m_w_pvalue)
    #print(m_w_statistic)
    #print(k_s_pvalue)
    #print(t_pvalue)
    
    #Bug in the Mann_Whitney p value calculation in scipy, so the p_value statistic is reported as nan
    ''' 
    pl.figure(1)
    pl.plot(r1_qual_distn)
    pl.show()
    '''
    
    #print(k_s_pvalue)
    #print(np.isnan(t_pvalue))
    #print(t_pvalue)
    #print(k_s_pvalue)
    
    if (k_s_pvalue < 0.05): # 95% confidence, was at 0.05
        '''
        This may not be the right test, but I couldn't find anything better for now (tried ChiSq and Fishers
        but can't use them as there's more than 2x2 categories
        Also I don't think the data are binned- it is frequencies for each Q score...
        '''
        #warnings.warn("Big difference in median quality between read1 and read2") # Was a median, but mann whitney tie correction broken in scipy
        print("Big difference in quality between read 1 and read 2")
    elif np.isnan(k_s_pvalue):
        print("One of the reads has a problem. Could not compare")
    
    '''
    pl.figure(1)
    pl.plot(r1_qual_distn)
    pl.figure(2)
    pl.plot(r2_qual_distn)
    #pl.figure(3)
    #pl.plot(r1_qual_raw)
    #pl.figure(4)
    #pl.plot(r2_qual_raw)
    pl.figure(5)
    pl.plot(r1_qual_raw_downsample)
    pl.figure(6)
    pl.plot(r2_qual_raw_downsample)
    pl.show()
    '''
    
    ##Abnormal patterns in data by cycle plot (% bases >Q30)
    #Generate a data by cycle plot

    #Locate the data which contains the quality information only
    #first_read_qual_subs
    #second_read_qual_subs
    ''' This was a check for the data match- it matches ok
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
    '''

    #Find the data for the first read
    #print(first_read_qual_subs)
    #read1_length
    #Try to replicate the above plot without the data extract- need proportion of cycle over Q30
    #Do an array division number Q30 over total number for each cycle

    #Sum each row to get Q30 values
    #Read 1
    #Need to convert arrays to float arrays or the resultant division will be nearest int (so all 0s)
    Q30_by_row_r1 = np.ndarray.astype(np.sum(Q30_r1_arr,axis=1),float)
    #print(Q30_by_row_r1)
    #print(len(Q30_by_row_r1))
    #Sum each row to get total values
    #Need to convert arrays to float arrays or the resultant division will be nearest int (so all 0s)
    total_by_row_r1 = np.ndarray.astype(np.sum(first_read_qual_subs,axis=1),float)
    proportion_Q30_r1 = np.divide(Q30_by_row_r1,total_by_row_r1)
    proportion_Q30_r1 = np.nan_to_num(proportion_Q30_r1)

    #print(proportion_Q30_r1[::14])

    #print(np.sum(proportion_Q30_r1))

    #pl.plot(proportion_Q30_r1)
    #pl.show()

    #Pull out the medians- remember this array is already sorted by cycle
    #First chunk the array into slices based on cycle:- start:stop:step
    #Test the slicing on the full array that has the cycles included- easier validation that it is working properly
    #print(first_read_qual[:(num_tls*num_surfaces):,:]) # This is correct- checked against excel spreadsheet
    #print(first_read_qual[:(num_tls*num_surfaces)+1,:]) # Testing that the above does stop where cycle switches from 1 to 2

    #Therefore here we have the part without the identifiers for the first read below
    #print(first_read_qual_subs[:(num_tls*num_surfaces):,:])
    #First thing to do is get the numbers for each quality bin over cycle
    #sum this array subset column-wise- this is the number of falling into each quality category, from Q01 to Q50
    ''' This was for the first cycle, but need to calculate this for all of the cycles- so within the loop
    cycle_qual_binned_vals = np.sum(first_read_qual_subs[:(num_tls*num_surfaces):,:],axis = 0)
    print(cycle_qual_binned_vals)
    '''
    #Test iterating through the cycles in chunks, cause that is what will need to do
    #and then nest the other things within in 

    '''
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

    #Tested using first_read_qual so that I could see the cycle numbers, now swapped over to first_read_qual_subs
    r1_qual_med = []
    Q30_median_over_cycle_r1 = []
    for qual_i,qual in enumerate(first_read_qual_subs[:,2][::(num_tls*num_surfaces)]):
        #print(iq)
        #print(iq*(num_tls*num_surfaces))
        #print(num_tls*num_surfaces) #This is 28 (which is 2*14 as expected)
        #print(first_read_qual[(iq*(num_tls*num_surfaces)),2])
        #print(first_read_qual[(iq*(num_tls*num_surfaces)):((iq*(num_tls*num_surfaces))+(num_tls*num_surfaces))]) #Checked and this is the final entry
        quality_chunk = (first_read_qual_subs[(qual_i*(num_tls*num_surfaces)):((qual_i*(num_tls*num_surfaces))+(num_tls*num_surfaces))])
        #print(quality_chunk)

        cycle_qual_binned_vals = np.sum(quality_chunk,axis = 0) #Checked is correct for first cycle
    
        #print(np.sum(quality_chunk,axis = 1))
        #print(np.mean(np.sum(quality_chunk,axis = 1)))
    
        #r1_med_qual_over_cycle.append(np.median(np.sum(quality_chunk,axis = 1)))
    
        '''
        print(cycle_qual_binned_vals)
        pl.plot(cycle_qual_binned_vals)
        pl.show()
        '''
    
        #Find the cumulative values on the array subset
        cycle_qual_binned_vals_cum = (np.cumsum(cycle_qual_binned_vals))

        #The median is at this position
        med_rank = (np.sum(cycle_qual_binned_vals)/2.0)
        #print(med_rank)
    
        #Proportion of total with this Q value
        #Create an array of suitable dimensions with the total
        #print(np.sum(cycle_qual_binned_vals))
        #print(np.divide(cycle_qual_binned_vals,))
        #Percentage of values falling into that Q value bin
        quality_percentage = ((cycle_qual_binned_vals*100)/(float(np.sum(cycle_qual_binned_vals))))
        #print(quality_percentage)
        #Low down qualities with high percentages
        '''
        From the colour coding on the Illumina SAV, I think we will be looking at 15% and over in any
        bin <Q30
        Have checked all percentages add up to 100
        '''
        #for perc in quality_percentage:
            #print(perc)
    
        #Set quality threshold for appearance in heatmap to 15
        qual_perc_o15 = np.where(quality_percentage > 15)
        #print(ans)
        #print(ans[0])
        #The Q score is ans+1 in this case as python is 0-indexed
        qual_perc_o15_under_Q30 = np.where(qual_perc_o15[0] < 29)
        #print(ans2)
        #print(ans2[0])
        #print(len(ans2))
        #print(ans2[0].size)
        #print(qual_i+1)
        #print(qual_perc_o15_under_Q30[0].size)
        if qual_perc_o15_under_Q30[0].size > 0:
            print("High percentage of total clusters under Q30 for cycle " + str(qual_i+1))
    
    
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
    
        #So the median of each cycle is- should get 101 of these
        #print(qual_med)
        r1_qual_med.append(qual_med) 
        #print(proportion_Q30_r1[::14])
        #print(np.sum(proportion_Q30_r1))
        #print(qual_i) #Runs through the number of cycles, so will want qual_i + num_tiles for segment
        #print(proportion_Q30_r1[qual_i])
        Q30_proportion_chunk = (proportion_Q30_r1[(qual_i*(num_tls*num_surfaces)):((qual_i*(num_tls*num_surfaces))+(num_tls*num_surfaces))])
        #print(Q30_proportion_chunk)
        #print(np.median(Q30_proportion_chunk))
        Q30_median_over_cycle_r1.append((np.median(Q30_proportion_chunk)))
        '''
        pl.plot(Q30_proportion_chunk)
        pl.show()
        '''
    r1_qual_med = np.asarray(r1_qual_med)
    Q30_median_over_cycle_r1 = np.asarray(Q30_median_over_cycle_r1)

    #Work out the degradation coefficient for the loss in quality over the read
    Q30_median_over_cycle_r1_xdata = (np.arange(1,(len(Q30_median_over_cycle_r1)+1))) # Want it to start at 1 and stop at 101
    #Fit a curve to the data
    #pl.plot(Q30_median_over_cycle_r1_xdata,Q30_median_over_cycle_r1)

    #function to fit- make it non-linear
    #Initial guesses for parameters
    p1 = 0.5
    p2 = 0.5

    '''
    def func(x, p1,p2):
        return p1*np.cos(p2*x) + p2*np.sin(p1*x)
    '''

    def func(x, p1,p2):
        return(p1 * x + p2) #Linear

    #def func_quad(x, p1,p2,p3):
        #return(p1 * x**2 + p2 * x + p3)

    #fit_func = func(Q30_median_over_cycle_r1_xdata, p1,p2)
    #print(fit_func)

    #p0_q = scipy.array([1,1,1])
    
    #This requires a function as input
    optimal_vals_Q30_r1, covar_Q30_r1 = curve_fit(func,Q30_median_over_cycle_r1_xdata,Q30_median_over_cycle_r1, p0=(p1,p2))
    #optimal_vals_Q30_r1_q, covar_Q30_r1_q = curve_fit(func_quad,Q30_median_over_cycle_r1_xdata,Q30_median_over_cycle_r1, p0_q)
    #popt, pcov = curve_fit(func, xdata, ydata,p0=(1.0,0.2))

    #Constrain the input values to exclude the outlying values at the beginning and end?- FUTURE WORK!!

    #pl.plot(fit_func)
    #pl.plot(-Q30_median_over_cycle_r1_xdata**2)

    #pred = (optimal_vals_Q30_r1[0]*np.cos(optimal_vals_Q30_r1[1]*Q30_median_over_cycle_r1_xdata)) + (optimal_vals_Q30_r1[1]*np.sin(optimal_vals_Q30_r1[0]*Q30_median_over_cycle_r1_xdata))
    linear_pred_r1 = (optimal_vals_Q30_r1[0] * Q30_median_over_cycle_r1_xdata + optimal_vals_Q30_r1[1])
    #quad_pred = (optimal_vals_Q30_r1_q[0] * Q30_median_over_cycle_r1_xdata**2 + optimal_vals_Q30_r1_q[1] * Q30_median_over_cycle_r1_xdata + optimal_vals_Q30_r1_q[2])

    #print(covar_Q30_r1)

    '''
    #Get the sum of squared residuals
    residuals_r1 = Q30_median_over_cycle_r1 - func(Q30_median_over_cycle_r1_xdata,optimal_vals_Q30_r1[0],optimal_vals_Q30_r1[1])
    fres = sum(residuals_r1**2)

    #print(fres) # Measure of how good a fit the model is
    '''

    #Print out the slope of the line
    slope_Q30_r1 = optimal_vals_Q30_r1[0]
    #print(slope_Q30_r1)

    #slope_Q30_r1 = -0.0006 #test


    if abs(slope_Q30_r1) > 0.0005:
        #warnings.warn("Big drop in quality towards the end of read 1")
        print("Big drop in quality towards the end of read 1")

    '''
    #Create a nice illustrative plot- remember this isn't going to give any information at all about individual outliers, only a worrying trend
    pl.figure(1)
    pl.plot(Q30_median_over_cycle_r1_xdata,Q30_median_over_cycle_r1,'.')
    pl.plot(Q30_median_over_cycle_r1_xdata,linear_pred_r1)
    
    pl.show()
    '''
    #pl.figure(3)
    #pl.plot(Q30_median_over_cycle_r1_xdata,quad_pred)

    #pl.show()

    #So the median for cycle 1 of read 1 is 
    #print(qual_med)- STOPPED THIS PRINTING OUT FOR NOW WHILE WAS WORKING ON SOMETHING ELSE
    #print(len(r1_qual_med)) # find out how many are stored- it is one per cycle

    '''
    print(first_read_qual_subs[::(num_tls*num_surfaces),:])
    print(len(first_read_qual_subs[::(num_tls*num_surfaces),:]))
    f = (len(first_read_qual_subs[::(num_tls*num_surfaces)]))
    '''

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
            Have checked all percentages add up to 100
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
    
            #So the median of each cycle is- should get 101 of these
            #print(qual_med)
            r2_qual_med.append(qual_med) 
            Q30_proportion_chunk = (proportion_Q30_r2[(qual_i*(num_tls*num_surfaces)):((qual_i*(num_tls*num_surfaces))+(num_tls*num_surfaces))])
            #print(Q30_proportion_chunk)
            #print(np.median(Q30_proportion_chunk))
            Q30_median_over_cycle_r2.append((np.median(Q30_proportion_chunk)))

        r2_qual_med = np.asarray(r2_qual_med)
        Q30_median_over_cycle_r2 = np.asarray(Q30_median_over_cycle_r2)

        #Work out the degradation coefficient for the loss in quality over the read
        Q30_median_over_cycle_r2_xdata = (np.arange(1,(len(Q30_median_over_cycle_r2)+1))) # Want it to start at 1 and stop at 101
        #Fit a curve to the data
        #function to fit- make it non-linear
        #Initial guesses for parameters- already above for r1, function also already defined above
        #This requires a function as input
        optimal_vals_Q30_r2, covar_Q30_r2 = curve_fit(func,Q30_median_over_cycle_r2_xdata,Q30_median_over_cycle_r2, p0=(p1,p2))
        linear_pred_r2 = (optimal_vals_Q30_r2[0] * Q30_median_over_cycle_r2_xdata + optimal_vals_Q30_r2[1])

        #Print out the slope of the line
        slope_Q30_r2 = optimal_vals_Q30_r2[0]
        #print(slope_Q30_r2)

        if abs(slope_Q30_r2) > 0.0005:
            #warnings.warn("Big drop in quality towards the end of read 2")
            print("Big drop in quality towards the end of read 2")

        '''
        #Create a nice illustrative plot- remember this isn't going to give any information at all about individual outliers, only a worrying trend
        pl.figure(2)
        pl.plot(Q30_median_over_cycle_r2_xdata,Q30_median_over_cycle_r2,'.')
        pl.plot(Q30_median_over_cycle_r2_xdata,linear_pred_r2)
        '''

        ##Do the degredation coefficient over r1 and r2 concatenated
        #This is not useful if there is no r2- currently nest within if clause
        #Concatenate the data for r1 and r2
        Q30_median_over_cycle_both = np.concatenate((Q30_median_over_cycle_r1,Q30_median_over_cycle_r2))
        Q30_median_over_cycle_both_xdata = (np.arange(1,(len(Q30_median_over_cycle_both)+1))) # Want it to start at 1 and stop at 101
        #Fit a curve to the data
        #function to fit- make it non-linear
        #Initial guesses for parameters- already above for r1, function also already defined above
        #This requires a function as input
        optimal_vals_Q30_both, covar_Q30_both = curve_fit(func,Q30_median_over_cycle_both_xdata,Q30_median_over_cycle_both, p0=(p1,p2))
        linear_pred_both = (optimal_vals_Q30_both[0] * Q30_median_over_cycle_both_xdata + optimal_vals_Q30_both[1])

        #Print out the slope of the line
        slope_Q30_both = optimal_vals_Q30_both[0]
        #print(slope_Q30_both)

        if abs(slope_Q30_both) > 0.0005:
            #warnings.warn("Big drop in quality towards the end of both of the reads")
            print("Big drop in quality towards the end of both of the reads")
        
        '''
        #Create a nice illustrative plot- remember this isn't going to give any information at all about individual outliers, only a worrying trend
        pl.figure(3)
        pl.plot(Q30_median_over_cycle_both_xdata,Q30_median_over_cycle_both,'.')
        pl.plot(Q30_median_over_cycle_both_xdata,linear_pred_both)
        '''
    
        '''Removed plot for now
        pl.plot(Q30_median_over_cycle_r2)
        pl.show()
        '''

        '''
        #Is this the same data as before (right up near the data extract)
        print(prop_Q30_r1)
        print(proportion_Q30_r1)
        print(np.mean(proportion_Q30_r1))
        print(prop_Q30_r2)
        print(proportion_Q30_r2)
        print(np.mean(proportion_Q30_r2))
        '''

    #Intensity over cycle information- means over all tiles- NOT ACTALLY USING THIS ATM
    cursor.execute(""" SELECT CycleID, Intensity_A, Intensity_C, Intensity_G, Intensity_T
                    FROM ExtractionMetrics
                    WHERE ExtractionMetrics.MiSeqRunID = """ + "'" + run_for_import + "'" """
                    ORDER BY ExtractionMetrics.MiSeqRunID, ExtractionMetrics.CycleID  """)
    intensity_cycles = cursor.fetchall()
    #print("Intensity for each base over cycle Retrieved")
    intensity_cycles_arr = np.asarray(intensity_cycles)
    #print(intensity_cycles_arr)
    #print(intensity_cycles_arr[:,0]) #cycle
    int_A_cycles = []
    int_C_cycles = []
    int_G_cycles = []
    int_T_cycles = []
    #Chunk this up into segments on cycle as before
    for int_i,int_cycle in enumerate(intensity_cycles_arr[:,0][::(num_tls*num_surfaces)]):
        #print(int_cycle)
        int_chunk = (intensity_cycles_arr[:,:][(int_i*(num_tls*num_surfaces)):((int_i*(num_tls*num_surfaces))+(num_tls*num_surfaces))])
        #print(int_chunk)
        #print(np.sum(int_chunk))
        int_A_cycles.append(np.mean(int_chunk[:,1]))
        int_C_cycles.append(np.mean(int_chunk[:,2]))
        int_G_cycles.append(np.mean(int_chunk[:,3]))
        int_T_cycles.append(np.mean(int_chunk[:,4]))
    #print(int_A_cycles)
    #print(int_C_cycles)
    #print(int_G_cycles)
    #print(int_T_cycles)
    #print(intensity_cycles_arr[:,0][::(num_tls*num_surfaces)]) # All cycle numbers once in an array

    #Removing the index reads and splitting into r1 and r2
    int_A_cycles_r1 = int_A_cycles[0:read1_length]
    int_A_cycles_r2 = int_A_cycles[(read1_length+ind_reads):(read1_length+ind_reads)+read2_length]
    int_C_cycles_r1 = int_C_cycles[0:read1_length]
    int_C_cycles_r2 = int_C_cycles[(read1_length+ind_reads):(read1_length+ind_reads)+read2_length]
    int_G_cycles_r1 = int_G_cycles[0:read1_length]
    int_G_cycles_r2 = int_G_cycles[(read1_length+ind_reads):(read1_length+ind_reads)+read2_length]
    int_T_cycles_r1 = int_T_cycles[0:read1_length]
    int_T_cycles_r2 = int_T_cycles[(read1_length+ind_reads):(read1_length+ind_reads)+read2_length]


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
    #(numtiles*numsurfaces) correspond to each index
    #print(index_metrics_arr)
    #print(index_metrics_arr[:,5])
    total_per_index = []
    for inde_i,inde in enumerate(index_metrics_arr[:,5][::(num_tls*num_surfaces)]):
        index_chunk = (index_metrics_arr[:,5][(inde_i*(num_tls*num_surfaces)):((inde_i*(num_tls*num_surfaces))+(num_tls*num_surfaces))])
        #print(index_chunk) #Tested correct with full index_metrics_arr (rather than just value)
        #Convert array to a numerical type- needed to exclude runid before doing this
        index_chunk_int = np.ndarray.astype(index_chunk,int)
        total_per_index.append(np.sum(index_chunk_int))
        #print("Next") #See above

    #print(index_metrics_arr[:,4][::(num_tls*num_surfaces)])

    #Obtain the total number of counts per sample (over all tiles) and then this as a proportion of total number
    #passing filter (which includes undetermined reads)
    total_per_index_arr = np.asarray(total_per_index)
    #print(total_per_index_arr)
    #print(reads_per_run_pf)
    prop_pf_per_index_arr = ((total_per_index_arr)/(float(reads_per_run_pf)*100)) # Integer division gives 0
    #print(prop_pf_per_index_arr)
    #print(np.sum(total_per_index_arr))
    ## This will enable (divided by the number of reads passing filter)- to get %reads identified (PF) from Indexing page of SAV
    #print(100*(np.sum(total_per_index_arr)/float(reads_per_run_pf))) #Note avoiding integer division = 0 again

    #Either/Or for labelling
    sample_names = index_metrics_arr[:,6][::(num_tls*num_surfaces)]  
    #Set the index names to the sequence of the indices
    #index_names = index_metrics_arr[:,4][::(num_tls*num_surfaces)]  
    #Set the index names to the name of the sample
    index_names = sample_names

    index_x_axis = np.arange(len(index_names)) #This is required for the later setting of xticks to labels

    ##Before deciding on the outlying samples, the NTC should be removed as it is a special case
    #It would still be good if it appeared on the plot though- this has been achieved
    location_of_ntc = []
    for samp_ind,samp in enumerate(sample_names):
        #find_ntc = re.compile("NTC") # This syntax could be useful for later
        '''
        print(samp)
        matches = re.findall("NTC", samp)
        mat = re.match("NTC", samp)
        se = re.search("NTC", samp)
        print(matches)
        print(mat)
        print(se)
        '''
        if re.search("ntc", samp, re.IGNORECASE):
            '''
            Find the NTC and remove it from the list of outlying samples, leaving only the samples
            which are over or under represented
            This version assumed that there was one NTC, amended to handle the case where there
            is more than one
            '''
            #print(samp)
            #print(samp_ind)
            #print(prop_pf_per_index_arr[samp_ind])
            #print(prop_pf_per_index_arr[0:samp_ind])
            #print(prop_pf_per_index_arr[(samp_ind+1):len(prop_pf_per_index_arr)])
            #Remove the NTC which will skew the data
            '''
            prop_pf_index_subs_arr = (np.concatenate((prop_pf_per_index_arr[0:samp_ind],prop_pf_per_index_arr[(samp_ind+1):len(prop_pf_per_index_arr)])))
            sample_names_subs = (np.concatenate((sample_names[0:samp_ind],sample_names[(samp_ind+1):len(sample_names)])))
            #Need to handle the case where there is >1 NTC
            location_of_ntc.append(samp_ind)
            n = samp_ind
            '''
            location_of_ntc.append(samp_ind)
        
        #else:
            #print(samp)
            # Only want to put these into the mean etc as the NTC should be treated as a special case

    #Create an array containing the NTC entries only
    #print(location_of_ntc)
    #location_of_ntc = [8,10] # This was for testing purposes: checking it worked if had more than 1 NTC
    prop_pf_index_ntc_arr = prop_pf_per_index_arr[location_of_ntc]
    sample_names_ntc = sample_names[location_of_ntc]
    #print(sample_names_ntc)
    #print(prop_pf_index_ntc_arr)
    ntc_arr = np.vstack((sample_names_ntc,prop_pf_index_ntc_arr)).T
    #print(ntc_arr) #Sample name and value in a 2D array
        
    #Create an array containing all the entries except the NTC ones        
    prop_pf_index_subs_arr = np.delete(prop_pf_per_index_arr,location_of_ntc)
    sample_names_subs = np.delete(sample_names,location_of_ntc)
    not_ntc_arr = np.vstack((sample_names_subs,prop_pf_index_subs_arr)).T
    #print(not_ntc_arr) #Sample name and value in a 2D array

    #print(prop_pf_per_index_arr)
    #print(prop_pf_index_subs_arr)
    ind_mean = (np.mean(prop_pf_index_subs_arr))
    #print(ind_mean)
    ind_std = (np.std(prop_pf_index_subs_arr))
    #print(ind_std)
    ind_high_threshold = (ind_mean + (2*ind_std))
    ind_low_threshold = (ind_mean - (2*ind_std))

    #Change threshold for testing purposes
    #ind_high_threshold = 5

    #print(np.where(prop_pf_per_index_arr > ind_high_threshold))
    #print(np.where(prop_pf_per_index_arr < ind_low_threshold))

    outlying_indexes = (np.where((prop_pf_index_subs_arr < ind_low_threshold) | (prop_pf_index_subs_arr > ind_high_threshold)))
    #print(outlying_indexes)
    #print(outlying_indexes[0])
    outlying_sample_indexes = (sample_names_subs[outlying_indexes[0]])
    #print(outlying_sample_indexes) #Checked correct against SAV
    #print(prop_pf_index_subs_arr[outlying_indexes[0]]) #This is the percentage of it
    #Concatenate the sample name and its value for later readout in a numpy array
    outlying_samples_values_arr = np.vstack((outlying_sample_indexes,prop_pf_index_subs_arr[outlying_indexes[0]])).T

    #np.savetxt("C:\Users\Sara\Dropbox\Bioinformatics Clinical Science\MScProject\PlayingWithExcelData\LookatMe.csv",arre, delimiter=",", fmt="%s")
    #outlying_sample_indexes = [] #Test for correct triggering of if clause below
    #print(np.where(outlying_sample_indexes != "NTC_15-13654"))

    #Coefficient of variation
    #print(ind_std)
    #print(ind_mean)
    index_COV = (ind_std/ind_mean)
    #print(index_COV)

    threshold_index_COV = 0.03 # Set to 3% otherwise very low samples won't trigger this (known because of COV value including NTC below)
                                # This is way too sensitive at the moment (Matt suggests 5%)

    if index_COV > threshold_index_COV:
        #warnings.warn("Big range over different sample indices") # Note that NTCs are excluded by this code
        print("Big range over different sample indices")

    '''
    #Work out COV including NTC- to see if matches Illumina's calculation
    ind_std_2 = np.std(prop_pf_per_index_arr)*100
    ind_mean_2 = np.mean(prop_pf_per_index_arr)*100
    index_COV_2 = (ind_std_2/ind_mean_2)
    print(np.min(prop_pf_per_index_arr))
    print(np.max(prop_pf_per_index_arr))
    print(index_COV_2) # This should be 0.4775 and comes out as 0.455
    '''

    if (len(outlying_indexes[0])) > 0:
        '''
        NEED TO WORK ON HOW TO PRESENT THIS DATA TO THE USER!! Also this is slightly redundant with the COV- but threshold is at 5% there, so this is more sensitive
        '''
        #warnings.warn("There is at least one outlying sample")
        print("There is at least one outlying sample")
        #print(outlying_samples_values_arr)
        low_num_reads_ind = (np.where(outlying_samples_values_arr[:,1] < ind_low_threshold))[0]
        #print(low_num_reads) #The index at which the low number of reads are found
        low_num_reads = (outlying_samples_values_arr[low_num_reads_ind,:])
        #print(low_num_reads) #The samples with proportions less than the low threshold in an array
        high_num_reads_ind = (np.where(outlying_samples_values_arr[:,1] > ind_high_threshold))[0]
        high_num_reads = (outlying_samples_values_arr[high_num_reads_ind,:])
        #print(high_num_reads) #The samples with proportions higher than the high threshold in an array
        '''
        if outlying_samples_values_arr[0][1] < ind_low_threshold:
            print("One sample has a very low number of reads")
        '''

    #Is the NTC elevated above baseline (i.e. is there contamination in the run?)
    NTC_threshold = 1.0
    '''
    print(ntc_arr)
    print(ntc_arr[:,1])
    print(prop_pf_index_ntc_arr)
    print(prop_pf_index_ntc_arr.any())
    '''

    if (len(np.where(prop_pf_index_ntc_arr > NTC_threshold)[0])) > 0: #If there is an entry in the array of the where
        #warnings.warn("NTC has a higher than expected proportion of reads")
        print("NTC has a higher than expected proportion of reads")

    '''
    print(location_of_ntc)
    print((sample_names[location_of_ntc],prop_pf_per_index_arr[location_of_ntc]))
    print((sample_names[n],prop_pf_per_index_arr[n]))
    print(ind_low_threshold)
    #if prop_pf_per_index_arr[location_of_ntc] > 0.5:
        #warnings.warn("NTC has a higher than expected proportion of reads")
    '''

    #pl.show()
    
    '''
    #Plot all the different indexes (all together)
    fig1 = pl.figure(1)
    ax1 = fig1.add_subplot(1,1,1) # one row, one column, first plot
    pl.xticks(index_x_axis,index_names)
    ax1.scatter(index_x_axis,prop_pf_per_index_arr)
    ax1.set_xlabel("Index")
    pl.show()
    '''
    '''
    #Plot intensity over cycle
    fig2 = pl.figure(2)
    #pl.plot((intensity_cycles_arr[:,0][::(num_tls*num_surfaces)]),int_A_cycles)
    pl.plot(int_A_cycles_r1)
    pl.plot(int_C_cycles_r1)
    pl.plot(int_G_cycles_r1)
    pl.plot(int_T_cycles_r1)

    fig3 = pl.figure(3)
    pl.plot(int_A_cycles_r2)
    pl.plot(int_C_cycles_r2)
    pl.plot(int_G_cycles_r2)
    pl.plot(int_T_cycles_r2)

    pl.show()
    '''

    '''
    pl.figure(11)
    f2 = pl.plot(proportion_Q30_r1)

    pl.figure(12)
    f3 = pl.plot(proportion_Q30_r2)

    pl.show()
    '''
    '''
    #Concatenate the arrays to get the same plot as the original data extract to double-check
    proportion_Q30_rboth = np.concatenate((proportion_Q30_r1,proportion_Q30_r2))
    pl.figure(13)
    f4 = pl.plot(proportion_Q30_rboth)


    #Do the median plots
    pl.figure(14)
    f5 = pl.plot(r1_qual_med)

    pl.figure(15)
    f6 = pl.plot(r2_qual_med)

    rboth_qual_med = np.concatenate((r1_qual_med,r2_qual_med))
    #print(len(rboth_qual_med)) #Correct length of 202 in this example, with reads of 101 cycles length
    pl.figure(16)
    f4 = pl.plot(rboth_qual_med)


    pl.show()
    '''

#Does it look how one would expect?

#Close the files?
#file_of_runs.close()
