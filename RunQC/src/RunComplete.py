'''
Created on Jan 21, 2016

@author: Sara
'''

class RunComplete(object):
    def __init__(self,username,password):
        import MySQLdb
        #self.MySQLdb = MySQLdb
        import sys
        import numpy as np
        self.np = np
        #self.sys
        #self.username = username
        #self.password = password
        try:
            db = MySQLdb.connect("localhost",username,password,"ngsqc" ) #Pass username and password as command line arguments
        except:
            sys.exit("Enter correct username and password!")
    
        #print("Successful connection")
        cursor = db.cursor()
        #self.db = db
        self.cursor = cursor
    
    def completeRun(self):
        print("t")
        return("t")
    
    def readLengths(self,run_for_import):
        #How long is each read?
        sql_command = """ SELECT ReadNumber, NumberOfCycles, Indexed
                    FROM Rds INNER JOIN LinkMiSeqRunRds
                    ON Rds.ReadID = LinkMiSeqRunRds.ReadID
                    WHERE LinkMiSeqRunRds.MiSeqRunID = """ + "'" + run_for_import + "'"
        self.cursor.execute(sql_command)
        reads_info = self.cursor.fetchall()
        reads_info_arr = self.np.array(reads_info)
        #Convert array from string type to integer type
        reads_info_arr_int = reads_info_arr.astype(int)
        print(reads_info_arr)
        '''
        ind_reads = 0
        for ind,read_extract in enumerate(reads_info_arr_int):   
            if read_extract[2] == 0:
            #Read is not an index read
            #print(read_extract[1])
                if (ind == 1) and (read_extract[1] == reads_info_arr_int[:,1].max()):
                    #R1 is the first one
                    read1_length = read_extract[1]
                elif (ind != 1) and (read_extract[1] == reads_info_arr_int[:,1].max()):
                    #R2 is the last one
                    read2_length = read_extract[1]
            elif read_extract[2] == 1:
                ind_reads += read_extract[1]
            else:
                raise Exception("Read is not properly identified as either not index or an index read")
    
    #How many reads there are from this way of counting them (all index reads and R1 and R2)
    num_cycles_reads = sum(reads_info_arr_int[:,1])
    '''
        