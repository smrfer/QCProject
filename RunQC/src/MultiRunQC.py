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

import RunComplete

#Load in a bunch of runs
#Later on this will trigger from Matt's transfer programme
#Connect to the database- user with select privileges only
try:
    db = MySQLdb.connect("localhost",sys.argv[1],sys.argv[2], "ngsqc" ) #Pass username and password as command line arguments

except:
    sys.exit("Enter correct username and password!")
    
#print("Successful connection")

cursor = db.cursor()

#Extract all the runs in the database
cursor.execute(""" SELECT MiSeqRun.MiSeqRunID
                    FROM MiSeqRun """)
runs_in_db = cursor.fetchall()
#print("List of runs extracted")

#Make a text file containing all these runs- let it create in base folder
outpath = sys.path[0]
outpath = outpath + "\\runs.txt"
outfile = open(outpath, 'w')
for run in runs_in_db:
    #print(x[0])
    print (run[0], file = outfile) # prints the run to a file identified by outfile
#print("List of runs generated")
outfile.close()

#Just for now use this as an example run- last run
run_for_import = run[0]
#Overwrite that as the run were looking at before- just for current testing purposes
run_for_import = '160104_M02641_0062_000000000-AL603'
print(run_for_import)


R = RunComplete.RunComplete(sys.argv[1],sys.argv[2])
print(R.completeRun())
print(R.readLengths(run_for_import))



#Maintain the database connection until the end of the file






