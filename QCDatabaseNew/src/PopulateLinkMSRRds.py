'''
Created on 11 Nov 2015

@author: Sara
'''
class PopLinker(object):
    def __init__(self,username,password):
        import MySQLdb
        import sys
        try:
            db = MySQLdb.connect("localhost",username,password, "ngsqc" ) #Pass username and password as command line arguments
        except:
            sys.exit("Enter correct username and password!")
        # prepare a cursor object using cursor() method
        cursor = db.cursor()
        #make variables
        self.db = db
        self.cursor = cursor

    def populateTable(self,read_num,indexed,num_cycles):
        sqlcommand = """ SELECT ReadID FROM Rds
            WHERE ReadNumber = """ + str(read_num) + " AND Indexed =  " + str(indexed) + \
            " AND NumberOfCycles = " + str(num_cycles)
            
            #NumberOfCycles = 151 AND Indexed = 0 AND ReadNumber = 1
        #print sqlcommand
        self.cursor.execute(sqlcommand)
        tmp = self.cursor.fetchall()
        return tmp[0][0]