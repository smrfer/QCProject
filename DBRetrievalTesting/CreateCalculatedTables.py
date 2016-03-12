'''
Created on 20 Nov 2015

@author: Sara
'''
import MySQLdb
import sys

try:
    db = MySQLdb.connect("localhost",sys.argv[1],sys.argv[2], "ngsqc" ) #Pass username and password as command line arguments

except:
    sys.exit("Enter correct username and password!")
    
print "Success so far"

# prepare a cursor object using cursor() method
cursor = db.cursor()

#Drop table if it already exists- figure out updating later
cursor.execute("""DROP TABLE IF EXISTS BinnedQualities""")
cursor.execute("""DROP TABLE IF EXISTS QualByRow""")

#NOTE THAT THIS DATA IS PERTAINING ONLY TO NEMO
#Create table with data in here
cursor.execute(""" CREATE TABLE BinnedQualities AS
                    SELECT GoodNemoData.MiSeqRunID,SUM(Q01) AS SQ01, SUM(Q01) AS SQ02, SUM(Q03) AS SQ03,
                    SUM(Q04) AS SQ04,SUM(Q05) AS SQ05,SUM(Q06) AS SQ06, SUM(Q07) AS SQ07, SUM(Q08) AS SQ08,
                    SUM(Q09) AS SQ09,SUM(Q10) AS SQ10,SUM(Q11) AS SQ11,SUM(Q12) AS SQ12,SUM(Q13) AS SQ13,
                    SUM(Q14) AS SQ14,SUM(Q15) AS SQ15,SUM(Q16) AS SQ16,SUM(Q17) AS SQ17,SUM(Q18) AS SQ18,
                    SUM(Q19) AS SQ19,SUM(Q20) AS SQ20,SUM(Q21) AS SQ21,SUM(Q22) AS SQ22,SUM(Q23) AS SQ23,
                    SUM(Q24) AS SQ24,SUM(Q25) AS SQ25,SUM(Q26) AS SQ26,SUM(Q27) AS SQ27,SUM(Q28) AS SQ28,
                    SUM(Q29) AS SQ29,SUM(Q30) AS SQ30,SUM(Q31) AS SQ31,SUM(Q32) AS SQ32,SUM(Q33) AS SQ33,
                    SUM(Q34) AS SQ34,SUM(Q35) AS SQ35,SUM(Q36) AS SQ36,SUM(Q37) AS SQ37,SUM(Q38) AS SQ38,
                    SUM(Q39) AS SQ39,SUM(Q40) AS SQ40,SUM(Q41) AS SQ41,SUM(Q42) AS SQ42,SUM(Q43) AS SQ43,
                    SUM(Q44) AS SQ44,SUM(Q45) AS SQ45,SUM(Q46) AS SQ46,SUM(Q47) AS SQ47,SUM(Q48) AS SQ48,
                    SUM(Q49) AS SQ49,SUM(Q50) AS SQ50
                    FROM QualityMetrics
                    INNER JOIN GoodNemoData ON GoodNemoData.MiSeqRunID = QualityMetrics.MiSeqRunID
                    GROUP BY QualityMetrics.MiSeqRunID """)

print "Table BinnedQualities created"

cursor.execute(""" CREATE TABLE QualByRow AS
                    SELECT GoodNemoData.MiSeqRunID,QualityMetrics.TileID,
                    QualityMetrics.CycleID,
                    (Q01)+(Q02)+(Q03)+(Q04)+(Q05)+(Q06)+(Q07)+(Q08)+
                    (Q09)+(Q10)+(Q11)+(Q12)+(Q13)+(Q14)+(Q15)+(Q16)+
                    (Q17)+(Q18)+(Q19)+(Q20)+(Q21)+(Q22)+(Q23)+(Q24)+
                    (Q25)+(Q26)+(Q27)+(Q28)+(Q29)+(Q30)+(Q31)+(Q32)+
                    (Q33)+(Q34)+(Q35)+(Q36)+(Q37)+(Q38)+(Q39)+(Q40)+
                    (Q41)+(Q42)+(Q43)+(Q44)+(Q45)+(Q46)+(Q47)+(Q48)+
                    (Q49)+(Q50)
                    AS TotalClusters,
                    (Q30)+(Q31)+(Q32)+(Q33)+(Q34)+(Q35)+(Q36)+(Q37)+
                    (Q38)+(Q39)+(Q40)+(Q41)+(Q42)+(Q43)+(Q44)+(Q45)+
                    (Q46)+(Q47)+(Q48)+(Q49)+(Q50)
                    AS ClustersOverQ30,
                    ((Q30)+(Q31)+(Q32)+(Q33)+(Q34)+(Q35)
                    +(Q36)+(Q37)+(Q38)+(Q39)+(Q40)+(Q41)+(Q42)+(Q43)+
                    (Q44)+(Q45)+(Q46)+(Q47)+(Q48)+(Q49)+(Q50)) /
                    ((Q01)+(Q02)+(Q03)+(Q04)+(Q05)+(Q06)+(Q07)+(Q08)+
                    (Q09)+(Q10)+(Q11)+(Q12)+(Q13)+(Q14)+(Q15)+(Q16)+
                    (Q17)+(Q18)+(Q19)+(Q20)+(Q21)+(Q22)+(Q23)+(Q24)+
                    (Q25)+(Q26)+(Q27)+(Q28)+(Q29)+(Q30)+(Q31)+(Q32)+
                    (Q33)+(Q34)+(Q35)+(Q36)+(Q37)+(Q38)+(Q39)+(Q40)+
                    (Q41)+(Q42)+(Q43)+(Q44)+(Q45)+(Q46)+(Q47)+(Q48)+
                    (Q49)+(Q50))
                    AS OverQ30
                    FROM QualityMetrics
                        INNER JOIN GoodNemoData ON GoodNemoData.MiSeqRunID = QualityMetrics.MiSeqRunID
                    GROUP BY QualityMetrics.MiSeqRunID, QualityMetrics.LaneID, 
                    QualityMetrics.TileID, QualityMetrics.CycleID""")

print "Table QualByRow created"


'''
Old QualByRow- all raw data
cursor.execute(""" CREATE TABLE QualByRow AS
                    SELECT NemoData.MiSeqRunID,(Q01)+(Q02)+(Q03)+(Q04)+(Q05)+(Q06)+
                    (Q07)+(Q08)+(Q09)+(Q10)+(Q11)+(Q12)+(Q13)+
                    (Q14)+(Q15)+(Q16)+(Q17)+(Q18)+(Q19)+(Q20)+
                    (Q21)+(Q22)+(Q23)+(Q24)+(Q25)+(Q26)+(Q27)+
                    (Q28)+(Q29)+(Q30)+(Q31)+(Q32)+(Q33)+(Q34)+
                    (Q35)+(Q36)+(Q37)+(Q38)+(Q39)+(Q40)+(Q41)+
                    (Q42)+(Q43)+(Q44)+(Q45)+(Q46)+(Q47)+(Q48)+
                    (Q49)+(Q50)
                    AS ItemSum
                    FROM QualityMetrics
                        INNER JOIN NemoData ON NemoData.MiSeqRunID = QualityMetrics.MiSeqRunID
                    GROUP BY QualityMetrics.MiSeqRunID, QualityMetrics.LaneID, 
                    QualityMetrics.TileID, QualityMetrics.CycleID""")

print "Table QualByRow created"
'''

'''
cursor.execute(""" CREATE TABLE QualByCyclePerRun AS
                    SELECT (Q01)+(Q02)+(Q03)+(Q04)+(Q05)+(Q06)+
                    (Q07)+(Q08)+(Q09)+(Q10)+(Q11)+(Q12)+(Q13)+
                    (Q14)+(Q15)+(Q16)+(Q17)+(Q18)+(Q19)+(Q20)+
                    (Q21)+(Q22)+(Q23)+(Q24)+(Q25)+(Q26)+(Q27)+
                    (Q28)+(Q29)+(Q30)+(Q31)+(Q32)+(Q33)+(Q34)+
                    (Q35)+(Q36)+(Q37)+(Q38)+(Q39)+(Q40)+(Q41)+
                    (Q42)+(Q43)+(Q44)+(Q45)+(Q46)+(Q47)+(Q48)+
                    (Q49)+(Q50)
                    AS ItemSum
                    FROM QualityMetrics
                        INNER JOIN NemoData ON NemoData.MiSeqRunID = QualityMetrics.MiSeqRunID
                    GROUP BY QualityMetrics.MiSeqRunID, QualityMetrics.LaneID, 
                    QualityMetrics.TileID, QualityMetrics.CycleID""")
print "Table QualByCyclePerRun created"
'''

#data = cursor.fetchall()