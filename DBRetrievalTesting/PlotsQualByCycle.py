'''
Created on 22 Nov 2015

@author: Admin
'''

import MySQLdb
import sys
import matplotlib.pyplot as pl
import numpy as np


# Open database connection- using a user that only has SELECT privileges to avoid accidentally dropping data
try:
    db = MySQLdb.connect("localhost",sys.argv[1],sys.argv[2], "ngsqc" ) #Pass username and password as command line arguments

except:
    sys.exit("Enter correct username and password!")
    
print "Success so far"

# prepare a cursor object using cursor() method
cursor = db.cursor()

cursor.execute(""" SELECT QualByRow.MiSeqRunID,QualByRow.CycleID,
                    AVG(OverQ30) AS AOverQ30
                    FROM QualByRow 
                    WHERE QualByRow.CycleID = QualByRow.CycleID
                    GROUP BY QualByRow.MiSeqRunID, QualByRow.CycleID """)
qual_cycle_data = cursor.fetchall()
print "Data Retrieved"
#print data

qual_cycle_array = np.asarray(qual_cycle_data)

print qual_cycle_array

#np.savetxt("C:\Users\Sara\Dropbox\Bioinformatics Clinical Science\MScProject\PlayingWithExcelData\Inspect.csv",qual_cycle_array, delimiter=",")

xdata = qual_cycle_array[:,1]
print xdata
print xdata[0]
print max(xdata)

#Work out what the xaxis labels should be
#xdata = np.arange(0,max(xdata)) #This actually looks the same as if do it as above

#Put y data into an array with each datapoint per row??
#Not yet completed

ydata = qual_cycle_array[:,2]
print ydata
print ydata[0]

pl.figure(1)
Figure = pl.plot(xdata,ydata)

#pl.figure(2)
#Figure2 = pl.plot(qual_cycle_array[:,1:2]) #This doesn't work as it fails with a x and y not having same first dimension error

pl.show()


