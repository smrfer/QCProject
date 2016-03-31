'''
Created on Jan 12, 2016

@author: Sara
'''
import os
import sys
import MySQLdb
import CheckExists as chk
import RunParamsUnix as RPU
import RunParametersParser as RP

#Set location of data for import to database
#base_dir = "C:\Users\Sara\Dropbox\Bioinformatics Clinical Science\MScProject\DataForQCDatabase\\"
base_dir = "C:\Users\Admin\Dropbox\Bioinformatics Clinical Science\MScProject\DataForQCDatabase\\"
#base_dir = "C:\Users\Sara\ownCloud\SAV Files\Dory\\"
#base_dir = "C:\Users\Sara\ownCloud\SAV Files\Nemo\\"

#Put in the types for the missing columns- not flexible atm- maybe make so later if needed
column_type_to_add = 'SMALLINT UNSIGNED' 

#Figure out which of the tables already exists
#Put the extra columns that you want for the MiSeqRun table in here
columns_to_add = ['NumTiles', 'NumSwaths', 'NumLanes', 'NumSurfaces']

# Don't actually need the MiSeqRunID for this one- really ought to take this out
# and put it in the relevant function, but don't want to break other things atm
checker = chk.CheckExists(' ', sys.argv[1],sys.argv[2])
missing_columns = checker.checkAdditionalData(columns_to_add)
#print missing_columns

#Connect to database
# Open database connection
try:
    db = MySQLdb.connect("localhost",sys.argv[1],sys.argv[2], "ngsqc" ) #Pass username and password as command line arguments

except:
    sys.exit("Enter correct username and password!")
    
print "Successful connection"

# prepare a cursor object using cursor() method
cursor = db.cursor()

#Only add an extra column if there's actually anything missing
if len(missing_columns) > 0:    
    for missing in missing_columns:
        #print missing
        cursor.execute(""" ALTER TABLE MiSeqRun 
                    ADD """ + missing + " " + column_type_to_add)
        db.commit()

print "Table Alteration complete"


#Put data into new columns- annoyingly this part just silently fails if there is no folder called base_dir    
for folder in os.listdir(base_dir):
    #print folder #Maybe print this later
    input_dir = base_dir + folder + "\\"
    interop_dir = input_dir + "\\InterOp\\"
    
    print folder #For troubleshooting purposes and seeing how far this has gone

    #Extract required data from runparameters file
    #Open up the class (initialise it with the correct data for each different piece of information)
    run_p_chk = RPU.IDRunParams(input_dir)
    filename_rp = run_p_chk.checkRP() #Gets the run parameters file, required to pull the RunID (see below)
    run_params = RP.RunParametersParser(filename_rp) # If there is no runparameters file an assertion error will be raised here
    num_tiles_per_swath = run_params.retrieveNestedRPData('Setup','NumTilesPerSwath')
    num_swaths = run_params.retrieveNestedRPData('Setup','NumSwaths')
    num_lanes = run_params.retrieveNestedRPData('Setup','NumLanes')
    #Retrieve the run id from the runparamaters file to avoid issues where folder has been incorrectly re-named
    this_run_id = run_params.retrieveRPData('RunID')
    name_surfaces = run_params.retrieveRPData('SurfaceToScan').lower() # handle any case differences which may arise
    if name_surfaces == 'both':
        num_surfaces = '2' # Needs to go in as a string- see examples of num_swaths etc
    else:
        num_surfaces = '1' # Needs to go in as a string- see examples of num_swaths etc
    
    ##Insert the data into the relevant columns of the database
    sqlcommand = """ UPDATE IGNORE MiSeqRun
                SET NumTiles = """  + num_tiles_per_swath + """,
                NumSwaths = """ + num_swaths + """,
                NumLanes = """ + num_lanes + """,
                NumSurfaces = """ + num_surfaces + """ 
                WHERE MiSeqRun.MiSeqRunID = """ + "'" + this_run_id + "'"
    cursor.execute(sqlcommand)
    db.commit()
db.close() 
print "Data append completed"