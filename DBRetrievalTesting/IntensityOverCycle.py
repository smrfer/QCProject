'''
Created on 25 Nov 2015

@author: Sara
'''
import MySQLdb
import sys
import matplotlib.pyplot as pl
import numpy as np

try:
    db = MySQLdb.connect("localhost",sys.argv[1],sys.argv[2], "ngsqc" ) #Pass username and password as command line arguments

except:
    sys.exit("Enter correct username and password!")
    
print "Connection Successful"

# prepare a cursor object using cursor() method
cursor = db.cursor()

#cursor.execute("""DROP TABLE IF EXISTS TABLENAME""")

cursor.execute("""  SELECT CycleID, AVG(Intensity_A), AVG(Intensity_C), 
                    AVG(Intensity_G), AVG(Intensity_T)
                    FROM ExtractionMetrics
                        INNER JOIN GoodNemoData ON ExtractionMetrics.MiSeqRunID = GoodNemoData.MiSeqRunID
                    GROUP BY ExtractionMetrics.MiSeqRunID,ExtractionMetrics.CycleID """)
intensity_data = cursor.fetchall()
print "Intensity Data Extracted"

intensity_data_arr = np.asarray(intensity_data)

pl.figure(1)
Figure = pl.plot(intensity_data_arr)

#Plot intensity data correctly- plot only A channel here

xdata = intensity_data_arr[:,0]
ydata =intensity_data_arr[:,1]

pl.figure(2)
Figure2 = pl.plot(xdata,ydata)

pl.show()

