'''
Created on 24 Jan 2016

@author: Admin
'''
#Required imports
from __future__ import print_function
import MySQLdb
import sys



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