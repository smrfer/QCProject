'''
Created on 12 Nov 2015

@author: Sara
'''

class PopulateBinaryTables(object):
    '''
    '''  
    def __init__(self,filepath,username,password):
        #Imports
        import ParseInterOpMetrics as pim
        self.pim = pim
        import RunParametersParser as RP
        self.RP = RP
        import RunParamsUnix as RPU
        self.RPU = RPU
        import sys
        import MySQLdb
        self.MySQLdb = MySQLdb
        import os
        self.os = os
        
        self.filepath = filepath
        self.username = username
        self.password = password
        
        try:
            db = self.MySQLdb.connect("localhost",username,password, "ngsqc" ) #Pass username and password as command line arguments

        except:
            sys.exit("Enter correct username and password!")
    
        # prepare a cursor object using cursor() method
        cursor = db.cursor()
        
        self.db = db
        self.cursor = cursor
    
    def extractData(self,encoding,supported_version,sqlcommand,binary_file):
        run_folder = self.filepath
        filename_bin = run_folder + "InterOp\\" + binary_file
        #print filename_bin
        
        #initialise runparams check class
        #run_p_chk = self.RPU.IDRunParams(run_folder + "\RunParameters.xml")
        run_p_chk = self.RPU.IDRunParams(run_folder)
        filename_rp = run_p_chk.checkRP() #Gets the run parameters file, required to pull the RunID (see below)
               
        
        #Sorting out the classes
        binary_data = self.pim.ParseInterOpMetrics(filename_bin)
        run_params = self.RP.RunParametersParser(filename_rp)
        #print "Working"

        #Pull the Run Name
        run_name = run_params.retrieveRPData('RunID')
        #print run_name

        #Pulling the data- read out bytearray
        entry_len = 0 #Put this outside of any loop
        offset = 0 #Put this outside of any loop
        cumulative_chunks = 0

        bytearr = binary_data.open_file_to_bytearray(filename_bin)
        readout_data_start = binary_data.convert_bytes(bytearr,supported_version)
        #print encoding
        
        #Having a pop at the loop
        while cumulative_chunks < (len(bytearr)-2): #Run through the bytearray
            offset = offset + entry_len #Need to get this one before entry len- is the summation of all previous entry lengths (on the first call the offset is 0)
            #print offset
            entry_len = binary_data.get_entry_len(bytearr) #This one is for the non-index binary files
            #print entry_len
            #print readout_data_start
            arr_segment = binary_data.get_array_segment(readout_data_start,bytearr,entry_len,offset)
            #print arr_segment
            #print encoding
            result_raw = binary_data.get_values_simple(encoding,arr_segment)
            cumulative_chunks += entry_len

            #print result_raw
            
            result_formatted = list(result_raw)
            
            #Handle the nans that crop up in SNR when all entries are 0 (presumably from division by 0)- replace by a 0
            #Can't store float nans in MySQL
            result_formatted = binary_data.handle_nan(result_formatted)
            
            result_formatted.append(run_name)
            #print result_formatted #Uncommenting this is useful for troubleshooting
            
            
            #Method using a placeholder to eliminate possibility of SQL injection (parameterization)
            self.cursor.executemany(sqlcommand, [result_formatted])
            
        self.db.commit() #This line has to be there or the changes don't happen!! Could also put db.autocommit(True) at the beginning
        self.db.close()
        
        return "Metrics extracted and table populated!"