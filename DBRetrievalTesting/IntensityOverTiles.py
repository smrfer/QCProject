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

cursor.execute(""" SELECT TileID, AVG(Intensity_A), AVG(Intensity_C), 
                    AVG(Intensity_G), AVG(Intensity_T)
                    FROM ExtractionMetrics
                        INNER JOIN GoodNemoData ON ExtractionMetrics.MiSeqRunID = GoodNemoData.MiSeqRunID
                    GROUP BY ExtractionMetrics.MiSeqRunID,ExtractionMetrics.TileID """)
intensity_data_tl = cursor.fetchall()
print "Intensity Data Extracted"

intensity_data_tl_arr = np.asarray(intensity_data_tl)

pl.figure(1)
Figure = pl.plot(intensity_data_tl_arr)

#Plot intensity data correctly- plot only A channel here

xdata = intensity_data_tl_arr[:,0]
ydata =intensity_data_tl_arr[:,1]
ydata2 =intensity_data_tl_arr[:,2]
ydata3 =intensity_data_tl_arr[:,3]
ydata4 =intensity_data_tl_arr[:,4]

pl.figure(2)
Figure2 = pl.plot(xdata,ydata)

#Plot from a single run
pl.figure(3)
Figure3 = pl.plot(xdata[0:14],ydata[0:14])
Figure3 = pl.plot(xdata[0:14],ydata2[0:14])
Figure3 = pl.plot(xdata[0:14],ydata3[0:14])
Figure3 = pl.plot(xdata[0:14],ydata4[0:14])

pl.show()


