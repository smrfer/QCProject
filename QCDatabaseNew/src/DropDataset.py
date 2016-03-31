'''
Created on 26 Feb 2016

@author: Admin
'''

#Script to drop a particular dataset
#Useful for when a dataset has been imported that you want to remove or re-add

import MySQLdb
import sys

#Enter dataset to delete here- two test sets, one with unique runs and other not
#to_delete = '130916_M00766_0050_000000000-A5M1U'
#to_delete = '160219_M00766_0011_000000000-AL6GM'
#to_delete = '151211_M00766_0169_000000000-AK5DW'
#to_delete = '130405_M00766_0006_000000000-A3FNU'
to_delete = ''

#Connect to the database- user with dropping privileges required
try:
    db = MySQLdb.connect("localhost",sys.argv[1],sys.argv[2], "ngsqc" ) #Pass username and password as command line arguments

except:
    sys.exit("Enter correct username and password!")

cursor = db.cursor()


#Foreign keys have been respecified to cascade deletes with the exception of the ReadID in the Rds table as this is also used by other datasets
#First find the ReadID for this dataset
#Use a parameterised query to try to avoid SQL injection
sql_cmd = """SELECT * FROM LinkMiSeqRunRds
                WHERE LinkMiSeqRunRds.MiSeqRunID = %s """
cursor.executemany(sql_cmd, [to_delete])
reads_del = cursor.fetchall()
rd_ids = [(i[2]) for i in reads_del] #tuple unpacking requires 2 entries only

#Find Rds entries where there is a single entry corresponding to the deleted run
lone_entry = []
for rd in rd_ids:
    sql_cmd = """SELECT COUNT(MiSeqRun.MiSeqRunID)
                FROM MiSeqRun
                INNER JOIN LinkMiSeqRunRds
                ON MiSeqRun.MiSeqRunID = LinkMiSeqRunRds.MiSeqRunID
                WHERE LinkMiSeqRunRds.ReadID = %s """
    cursor.executemany(sql_cmd, [rd])
    ids = cursor.fetchall()
    if ids[0][0] < 2:
        lone_entry.append(rd)

#'''
#Delete all data associated with this run
#Use a parameterised query to try to avoid SQL injection
sql_cmd = """DELETE FROM IndexMetricsMSR
                WHERE IndexMetricsMSR.MiSeqRunID = %s """
cursor.executemany(sql_cmd, [to_delete])
print "IndexMetrics deleted"

sql_cmd = """DELETE FROM TileMetrics
                WHERE TileMetrics.MiSeqRunID = %s """
cursor.executemany(sql_cmd, [to_delete])
print "TileMetrics deleted"

sql_cmd = """DELETE FROM ErrorMetrics
                WHERE ErrorMetrics.MiSeqRunID = %s """
cursor.executemany(sql_cmd, [to_delete])
print "ErrorMetrics deleted"

sql_cmd = """DELETE FROM CorrectedIntMetrics
                WHERE CorrectedIntMetrics.MiSeqRunID = %s """
cursor.executemany(sql_cmd, [to_delete])
print "CorrectedIntMetrics deleted"

sql_cmd = """DELETE FROM ExtractionMetrics
                WHERE ExtractionMetrics.MiSeqRunID = %s """
cursor.executemany(sql_cmd, [to_delete])
print "ExtractionMetrics deleted"

sql_cmd = """DELETE FROM QualityMetrics
                WHERE QualityMetrics.MiSeqRunID = %s """
cursor.executemany(sql_cmd, [to_delete])
print "QualityMetrics deleted"

sql_cmd = """DELETE FROM LinkMiSeqRunRds
                WHERE LinkMiSeqRunRds.MiSeqRunID = %s """
cursor.executemany(sql_cmd, [to_delete])
print "LinkMiSeqRunRds deleted"

sql_cmd = """DELETE FROM MiSeqRun
                WHERE MiSeqRun.MiSeqRunID = %s """
cursor.executemany(sql_cmd, [to_delete])
print "MiSeqRun deleted"

#'''
            
#Delete any lone Rds entries as we don't want them cluttering up the database
if len(lone_entry) > 0:
    print "Lone Entry detected"
    additional = ((len(lone_entry)-1)*' OR Rds.ReadID = %s')
    sql_cmd = """DELETE FROM Rds
                WHERE Rds.ReadID = %s """ + additional
    cursor.executemany(sql_cmd, [lone_entry])

print "Changes to " + to_delete + " complete"
db.commit() #This line has to be there or the changes don't happen!! Could also put db.autocommit(True) at the beginning
db.close()    
