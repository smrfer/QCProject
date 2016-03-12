'''
Created on 17 Nov 2015

@author: Sara
'''
import MySQLdb
import sys
import matplotlib.pyplot as pl
import numpy as np
from scipy import stats


# Open database connection- using a user that only has SELECT privileges to avoid accidentally dropping data
try:
    db = MySQLdb.connect("localhost",sys.argv[1],sys.argv[2], "ngsqc" ) #Pass username and password as command line arguments

except:
    sys.exit("Enter correct username and password!")
    
print "Success so far"

# prepare a cursor object using cursor() method
cursor = db.cursor()

cursor.execute(""" SELECT SQ01,SQ02,SQ03,SQ04,SQ05,SQ06,SQ07,SQ08,SQ09,SQ10,SQ11,SQ12,SQ13,SQ14,SQ15,SQ16,SQ17,
                    SQ18,SQ19,SQ20,SQ21,SQ22,SQ23,SQ24,SQ25,SQ26,SQ27,SQ28,SQ29,SQ30,SQ31,SQ32,SQ33,SQ34,SQ35,
                    SQ36,SQ37,SQ38,SQ39,SQ40,SQ41,SQ42,SQ43,SQ44,SQ45,SQ46,SQ47,SQ48,SQ49,SQ50
                    FROM BinnedQualities """)
data = cursor.fetchall()
print "Data Retrieved"
#print data

arr = np.asarray(data)
#print arr

#colsum = arr[2].sum()

#print colsum

#print arr.sum()

total_clusters = arr.sum(axis=1)

#print total_clusters

normalised_arr = arr / total_clusters[:,np.newaxis]
#Dump out normalised array for playing with
#np.savetxt("C:\Users\Sara\Dropbox\Bioinformatics Clinical Science\MScProject\PlayingWithExcelData\NormQualPerRun.csv",normalised_arr, delimiter=",")

#print normalised_arr[35]
#print np.mean(normalised_arr[35])
#print np.median(normalised_arr[35])
#print stats.mode(normalised_arr[35])

mns = []
sts = []
meds = []
med_iqr = []
mn_sts = []
#This was doing it in rows instead of in colummns- transposing in forloop initiation didn't seem to work. Have to transpose before like this.
normalised_arr = normalised_arr.T
for ind,col in enumerate(normalised_arr): #Makes columns rows
    #print ind
    #print col
    mn = np.mean(normalised_arr[ind])
    st = np.std(normalised_arr[ind])
    med = np.median(normalised_arr[ind])
    q75 = np.percentile(normalised_arr[ind], 75, interpolation='higher')
    q25 = np.percentile(normalised_arr[ind], 25, interpolation='lower')
    iqr = q75 - q25
    mns.append([mn])
    meds.append([med])
    med_iqr.append([med,iqr])
    mn_sts.append([mn,st])
#print med_iqr
 
#Best approach is to build lists and then convert to numpy array as if make array requires re-creation at each stage (no append)    
meds_arr = np.asarray(meds)
mns_arr = np.asarray(mns)
med_iqr_arr = np.asarray(med_iqr)
mn_sts_arr = np.asarray(mn_sts)
#print med_iqr_arr
#np.savetxt("C:\Users\Sara\Dropbox\Bioinformatics Clinical Science\MScProject\PlayingWithExcelData\Inspect.csv",med_iqr_arr, delimiter=",")

pl.figure(1)
pl.plot(med_iqr_arr)

pl.figure(2)
pl.plot(mn_sts_arr)

pl.figure(3)
pl.plot(meds_arr)
pl.plot(mns_arr)

x = np.arange(0,50)
pl.figure(4)
Fig1 = pl.plot(x,arr[:,:].T)

pl.show()

'''  
pl.figure(3)
pl.plot(normalised_arr)

pl.show()
'''

'''
pl.figure(2)
density = stats.kde.gaussian_kde(normalised_arr[35])
pl.plot(density)
'''
#pl.show()





#for num in xrange(82):
    #print num
    #pl.figure(num)
    #pl.plot(arr[num])

#pl.show()



'''

#print arr[5]
x = np.arange(0,50)
pl.figure(1)
Fig1 = pl.plot(x,arr[:,:].T)

pl.figure(2)
#ax = pl.gca()
#ax.set.xticks([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50])
#ax.set_autoscale_on(False)
Fig2 = pl.plot(x,normalised_arr[:,:].T)

pl.figure(3)
Fig3 = pl.plot(arr[1])


#pl.figure(4)
#Fig4 = pl.plot(arr2)

#pl.figure(4)
#Fig4 = pl.plot(x,arr[:,:]) #This doesn't work. Need to transpose

pl.show()

#print "Selected"
'''







