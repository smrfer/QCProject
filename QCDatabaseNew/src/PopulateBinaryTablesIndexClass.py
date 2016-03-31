'''
Created on 10 Nov 2015

@author: Admin
'''
class PopulateBinaryTablesIndex(object):
    
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
        
    def extractData(self):    
        run_folder = self.filepath
        filename_bin = run_folder + "InterOp\IndexMetricsOut.bin"
        
        #initialise runparams check class
        #run_p_chk = self.RPU.IDRunParams(run_folder + "\RunParameters.xml")
        run_p_chk = self.RPU.IDRunParams(run_folder)
        filename_rp = run_p_chk.checkRP() #Gets the run parameters file, required to pull the RunID (see below)
            
        supported_version_number = 1
        encoding = "HHHHYsIHVsHWs" #Known encoding from SAV guide

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
        readout_data_start = binary_data.convert_bytes_index(bytearr,supported_version_number)
        
        #Having a pop at the loop
        while cumulative_chunks < (len(bytearr)-1): #Run through the bytearray
            offset = offset + entry_len #Need to get this one before entry len- is the summation of all previous entry lengths (on the first call the offset is 0)
            Y_pos = binary_data.get_Y(readout_data_start,bytearr,offset)
            V_pos = binary_data.get_V(readout_data_start,bytearr,offset)
            W_pos = binary_data.get_W(readout_data_start,bytearr,offset)
            entry_len = binary_data.get_entry_len_ind(readout_data_start,bytearr,offset)
            arr_segment = binary_data.get_array_segment(readout_data_start,bytearr,entry_len,offset)
            encoding_string = binary_data.get_encoding_string_var(Y_pos,V_pos,W_pos,encoding)
            result_raw = binary_data.get_values_simple(encoding_string,arr_segment)
            cumulative_chunks += entry_len
            ses = binary_data.get_s(encoding_string)
            result_formatted = binary_data.get_formatted_values(Y_pos,V_pos,W_pos,ses,result_raw)
    
            result_formatted.append(run_name)
            #print result_formatted

            #Method using a placeholder to eliminate possibility of SQL injection (parameterization)
            sqlcommand= """ INSERT IGNORE INTO IndexMetricsMSR
                            (LaneID,TileID,ReadNum,IndexName,NumControlClusters,SampleName,ProjectName,MiSeqRunID)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""" #%s is the placeholder for a string
            self.cursor.executemany(sqlcommand, [result_formatted])
    
        self.db.commit() #This line has to be there or the changes don't happen!! Could also put db.autocommit(True) at the beginning
        self.db.close()
        return "Index metrics extracted and table populated!"