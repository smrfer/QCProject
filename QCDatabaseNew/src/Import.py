'''
Created on 10 Nov 2015

@author: Admin
'''
import os
import sys
import PopulateBinaryTablesIndexClass as bin_ind
import PopulateBinaryTablesExtractionClass as bin_ext
import PopulateBinaryTablesClass as bin_f
import PopulateTablesClass as tbls
import CheckExists as chk

#base_dir = "F:\SAV\\"
#base_dir = "C:\Users\Sara\Dropbox\Bioinformatics Clinical Science\MScProject\\0STUFF\\"
base_dir = "C:\Users\Admin\Dropbox\Bioinformatics Clinical Science\MScProject\DataForQCDatabase\\"
#base_dir = "C:\Users\Sara\Dropbox\Bioinformatics Clinical Science\MScProject\DataForQCDatabase\\"
#base_dir = "G:\DataForQCDatabase\\"
#base_dir = "E:\DataForQCDatabase\\"
#base_dir = "G:\DataForQCDatabase-Additional\\"
#base_dir = "E:\SAVData\\"
#base_dir = "E:\PhiXRuns\\"
#base_dir = "F:\Temp\\"
#base_dir = "C:\Users\Admin\Dropbox\Bioinformatics Clinical Science\OLAT rotations\Years Two-Three\SAVWork\PhiXRuns\\"

#base_dir = "C:\Users\Sara\Dropbox\Bioinformatics Clinical Science\OLAT rotations\Years Two-Three\SAVWork\PhiXRuns\\"
#base_dir = "C:\Users\Admin\Dropbox\Bioinformatics Clinical Science\OLAT rotations\Years Two-Three\SAVWork\PhiXRuns\\150818_M00766_0125_000000000-AE8BP\\"
#150224_M00766_0078_000000000-ACMP5

for folder in os.listdir(base_dir):
    #print folder #Maybe print this later
    input_dir = base_dir + folder + "\\"
    interop_dir = input_dir + "\\InterOp\\"
    
    print folder #For troubleshooting purposes and seeing how far this has gone
    
    #Skip parsing any files if there's already an entry with that name
    try:
        chk_exists = chk.CheckExists(folder,sys.argv[1],sys.argv[2])
        exists = chk_exists.checkData()
        if exists:
            print "Already In"
        else:
            #COMMENTED OUT FOR TESTING SKIP IMPORT
            #Initialise class for import from non-binary files
            #(Need to initialise for each binary import separately or database close connection means can't populate)
            populate_tables = tbls.PopulateTables(input_dir,sys.argv[1],sys.argv[2])
    
            #Populate the MiSeqRun, Reads and Linker tables
            populate_tables.populateTables()
    
            #Populate the binary files tables
            for file_n in os.listdir(interop_dir):
                #print file
                if file_n == "CorrectedIntMetricsOut.bin":
                    #Initialise binary class
                    binaries = bin_f.PopulateBinaryTables(input_dir,sys.argv[1],sys.argv[2])
                    encoding = "HHHHHHHHHHHHLLLLLf"
                    supported_version = 2
                    sqlcommand = """ INSERT IGNORE INTO CorrectedIntMetrics
                            (LaneID,TileID,CycleID,AverageIntensity,AverageCorrectedIntensity_A,
                            AverageCorrectedIntensity_C,AverageCorrectedIntensity_G,AverageCorrectedIntensity_T,
                            AverageCorrectedIntensityCalledClusters_A,AverageCorrectedIntensityCalledClusters_C,
                            AverageCorrectedIntensityCalledClusters_G,AverageCorrectedIntensityCalledClusters_T,
                            NumNoCalls,NUM_A,NUM_C,NUM_G,NUM_T,Signal2NoiseRatio,MiSeqRunID)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """ #%s is the placeholder for a string
                    metrics = binaries.extractData(encoding,supported_version,sqlcommand,"CorrectedIntMetricsOut.bin")
                elif file_n == "ExtractionMetricsOut.bin":
                    #Initialise class
                    extraction = bin_ext.PopulateBinaryExtractionTables(input_dir,sys.argv[1],sys.argv[2])
                    ext_metrics = extraction.extractData()
                elif file_n == "IndexMetricsOut.bin":
                    #call the PopulateBinaryTablesIndex script- fixed
                    #Initialise class
                    index = bin_ind.PopulateBinaryTablesIndex(input_dir,sys.argv[1],sys.argv[2])
                    ##COMMENTING THIS ONE OUT
                    the_index_data = index.extractData() #Need this back in for the real show!!!!
                    #print the_index_data - here to see the extracted data
                    #continue
                elif file_n == "QMetricsOut.bin": #THIS ISN@T WORKING ATM- something to do with closing the database then wanting to reconnect?
                    #Initialise binary class
                    binaries = bin_f.PopulateBinaryTables(input_dir,sys.argv[1],sys.argv[2])
                    encoding = "HHHIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"
                    supported_version = 4
                    sqlcommand = """ INSERT IGNORE INTO QualityMetrics
                            (LaneID,TileID,CycleID,Q01,Q02,Q03,Q04,Q05,Q06,Q07,Q08,Q09,Q10,Q11,Q12,
                            Q13,Q14,Q15,Q16,Q17,Q18,Q19,Q20,Q21,Q22,Q23,Q24,Q25,Q26,Q27,Q28,Q29,Q30,
                            Q31,Q32,Q33,Q34,Q35,Q36,Q37,Q38,Q39,Q40,Q41,Q42,Q43,Q44,Q45,Q46,Q47,Q48,Q49,Q50,MiSeqRunID)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """ #%s is the placeholder for a string
                    metrics = binaries.extractData(encoding,supported_version,sqlcommand,"QMetricsOut.bin")
                elif file_n == "ErrorMetricsOut.bin":
                    #Initialise binary class
                    binaries = bin_f.PopulateBinaryTables(input_dir,sys.argv[1],sys.argv[2])
                    encoding = "HHHfIIIII"
                    supported_version = 3
                    sqlcommand = """ INSERT IGNORE INTO ErrorMetrics
                            (LaneID,TileID,CycleID,ErrorRate,NumPerfectRds,NumSingleError,NumDoubleError,
                            NumTripleError,NumQuadrupleError,MiSeqRunID)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """ #%s is the placeholder for a string
                    metrics = binaries.extractData(encoding,supported_version,sqlcommand,"ErrorMetricsOut.bin")
                elif file_n == "TileMetricsOut.bin":
                    #Initialise binary class
                    binaries = bin_f.PopulateBinaryTables(input_dir,sys.argv[1],sys.argv[2])
                    encoding = "HHHf"
                    supported_version = 2
                    sqlcommand = """ INSERT IGNORE INTO TileMetrics
                            (LaneID,TileID,CodeID,Value,MiSeqRunID)
                            VALUES (%s,%s,%s,%s,%s) """ #%s is the placeholder for a string
                    metrics = binaries.extractData(encoding,supported_version,sqlcommand,"TileMetricsOut.bin")
                else:
                    #These are the files present that are not being read out
                    #print file_n #MAYBE READ THIS OUT TO A FILE WITH THE ASSOCIATED RUN NAME!!!!!!!!!!!!!!
                    continue
    except IndexError:
        raise Exception("Enter username and password for database connectivity as arguments 1 and 2 when running this script")              
    print "Import complete"