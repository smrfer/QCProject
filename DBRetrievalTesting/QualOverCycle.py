'''
Created on 24 Nov 2015

@author: Sara
'''
import MySQLdb
import sys

try:
    db = MySQLdb.connect("localhost",sys.argv[1],sys.argv[2], "ngsqc" ) #Pass username and password as command line arguments

except:
    sys.exit("Enter correct username and password!")
    
print "Connection Successful"

# prepare a cursor object using cursor() method
cursor = db.cursor()

cursor.execute("""DROP TABLE IF EXISTS ClusterByCycle""")
cursor.execute("""DROP TABLE IF EXISTS TotalClusters""")

#Make these temporary tables when finalise
#This is not working as expected- gives the same value for each cycle- actually this is correct- not properly specified what want!!! Checked in Excel
cursor.execute(""" CREATE TABLE ClusterByCycle AS
                    SELECT QualByRow.MiSeqRunID,QualByRow.CycleID,
                    SUM(TotalClusters) AS SClustersCycle
                    FROM QualByRow 
                    WHERE QualByRow.CycleID = QualByRow.CycleID
                    GROUP BY QualByRow.MiSeqRunID, QualByRow.CycleID""")
print "Table ClusterByCycle created"


#Query to sum over the data for an entire run
cursor.execute(""" CREATE TABLE TotalClusters AS
                    SELECT QualByRow.MiSeqRunID,
                    SUM(TotalClusters) AS SClusters
                    FROM QualByRow 
                    WHERE QualByRow.MiSeqRunID = QualByRow.MiSeqRunID
                    GROUP BY QualByRow.MiSeqRunID""")
print "Table TotalClusters created"


cursor.execute(""" SELECT ClusterByCycle.MiSeqRunID, ClusterByCycle.CycleID,
                            ClusterByCycle.SClustersCycle, TotalClusters.SClusters
                    FROM ClusterByCycle
                        INNER JOIN TotalClusters
                        ON ClusterByCycle.MiSeqRunID = TotalClusters.MiSeqRunID""")
print "Data Selected"





'''
SELECT QualByRow.MiSeqRunID,QualByRow.TileID,QualByRow.CycleID,
SUM(TotalClusters) AS SClusters
FROM QualByRow 
WHERE QualByRow.CycleID = QualByRow.CycleID
GROUP BY QualByRow.MiSeqRunID, QualByRow.CycleID
'''