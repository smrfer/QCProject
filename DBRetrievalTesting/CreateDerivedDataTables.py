'''
Created on 20 Nov 2015

@author: Sara
'''
import MySQLdb
import sys

# Open database connection
try:
    db = MySQLdb.connect("localhost",sys.argv[1],sys.argv[2], "ngsqc" ) #Pass username and password as command line arguments

except:
    sys.exit("Enter correct username and password!")
    
print "Success so far"

# prepare a cursor object using cursor() method
cursor = db.cursor()

#Drop view if it already exists- figure out updating later
cursor.execute("""DROP VIEW IF EXISTS NemoData""")
cursor.execute("""DROP VIEW IF EXISTS GoodNemoData""")

#Create a view with only data from Nemo
cursor.execute(""" CREATE VIEW NemoData AS
                    SELECT *
                    FROM MiSeqRun
                    WHERE MiSeqRun.Instrument = 'M00766' """)

print "Population of view 'NemoData' complete"


cursor.execute(""" CREATE VIEW GoodNemoData AS
                    SELECT *
                    FROM NemoData
                    WHERE NemoData.RunStartDate NOT BETWEEN '2014-10-15' AND '2015-02-05'
                    AND NemoData.RunStartDate NOT BETWEEN '2015-09-20' AND '2015-10-08'
                    AND NemoData.RunStartDate NOT BETWEEN '2014-07-21' AND '2014-07-31' """)
print "Population of view 'GoodNemoData' complete"

