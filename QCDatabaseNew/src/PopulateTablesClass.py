'''
Created on 12 Nov 2015

@author: Admin
'''
class PopulateTables(object):
    def __init__(self,file_directory,username,password):
        import MySQLdb
        self.MySQLdb = MySQLdb
        import sys
        import SampleSheetParser as ssp
        self.ssp = ssp
        import RunParametersParser as RP
        self.RP = RP
        import RunParamsUnix as RPU
        self.RPU = RPU
        import SampleSheetCheck as SSC
        self.SSC = SSC
        import PopulateLinkMSRRds as link
        self.link = link
        
        self.username = username
        self.password = password
        self.file_directory = file_directory
        
        
        try:
            db = self.MySQLdb.connect("localhost",username,password,"ngsqc" ) #Pass username and password as command line arguments

        except:
            sys.exit("Enter correct username and password!")
    
        # prepare a cursor object using cursor() method
        cursor = db.cursor()
        
        self.db = db
        self.cursor = cursor
        
    def populateTables(self):
        run_p_chk = self.RPU.IDRunParams(self.file_directory)
        filename_rp = run_p_chk.checkRP() #Gets the run parameters file, required to pull the RunID (see below)
        
        run_params = self.RP.RunParametersParser(filename_rp)
        
        #SampleSheet
        #Check sample sheet is there
        #Initialise samplesheet check class
        ss = self.SSC.SampleSheetChk(self.file_directory)
        ss_check = ss.checkSS()
       
        sample_sheet = self.ssp.SampleSheetParser(ss_check)
        
        #Use the functions within the class
        run_id = run_params.retrieveRPData('RunID')
        run_start_date = run_params.retrieveRPData('RunStartDate')
        run_number = run_params.retrieveRPData('RunNumber')
        instrument = run_params.retrieveRPData('ScannerID')
        fpga = run_params.retrieveRPData('FPGAVersion')
        mcs = run_params.retrieveRPData('MCSVersion')
        rta = run_params.retrieveRPData('RTAVersion')
        reagent_kit = run_params.retrieveRPData('ReagentKitVersion')[-1] #-1 to just put the value (X) in rather than VersionX
        chemid = run_params.retrieveRPData('Chemistry')
        onboard_analysis = run_params.retrieveNestedRPData('Workflow','Analysis')
        
        #print run_id #Just to see which one fails if any
        
        #Get flowcell, PR2 and ReagentKit data- ORDER IN LIST IS IMPORTANT TO LATER POPULATING THE DATABASE
        nested_list = []
        for item in ['FlowcellRFIDTag','PR2BottleRFIDTag','ReagentKitRFIDTag']:
            for identifier in ['SerialNumber','PartNumber','ExpirationDate']:
                if identifier == 'ExpirationDate':
                    nested_list.append(run_params.retrieveNestedRPData(item,identifier)[0:10]) #To exclude the T00:00:00 part
                else:
                    nested_list.append(run_params.retrieveNestedRPData(item,identifier))
        #print nested_list
        
        #Handle the cases where there is no sample sheet available. This can happen as it wasn't a
        #requirement for the SAV viewer, so some runs I don't have the sample sheet available
        try:
            worksheet = sample_sheet.getWorksheetNumber()
            investigator = sample_sheet.getInvestigatorName()
            pipeline = sample_sheet.getPipelineName() #This could be null- need to handle in the samplesheet parser class
        
        except:
            worksheet = ' '
            investigator = ' '
            pipeline = ' '
        
        #Stuff to populate the reads table
        read_num = run_params.getNumSubelements('Reads') #Count number of reads that need to be entered for this run

        reads_list = run_params.returnElementInfo('Reads','Number','IsIndexedRead','NumCycles')

        #From the previously found number of reads for this sample, create the correct formatting for 
        #the database insertion placeholder
        get_num_rds = ('(%s,%s,%s),' * read_num).rstrip(',') #Known 3 entries for Rds table (3 subelements) and then strip trailing comma 

        #Populate the Rds table- (have added a unique composite constraint to prevent repeat adding)
        sqlcommand = """ INSERT IGNORE INTO Rds
                    (ReadNumber,Indexed,NumberOfCycles)
                    VALUES """ + str(get_num_rds)
        self.cursor.executemany(sqlcommand, [reads_list])
        self.db.commit() 

        num_entries_rds_tbl = 3 #Known that there are 3 fields to populate in the Rds table (see above)

        #Method using a placeholder to eliminate possibility of SQL injection (parameterization)- insert data into MiSeqRun table
        datalist = [run_id,run_start_date,run_number,instrument,fpga,mcs,rta,reagent_kit,
                    onboard_analysis,worksheet,investigator,chemid,pipeline]
        new_datalist = datalist + nested_list
        s_placeholders = ('%s,' * len(new_datalist)).rstrip(',') #Get required number of placeholders, strip trailing comma

        sqlcommand = """ INSERT IGNORE INTO MiSeqRun
                (MiSeqRunID,RunStartDate,RunNumber,Instrument,FPGAVersion,MCSVersion,RTAVersion,KitVersionNumber,
                OnboardAnalysis,ExperimentName,Operator,Chemistry,Pipeline,FlowCell,FlowCellPartID,FlowCellExpiry,
                PR2Bottle,PR2BottlePartID,PR2BottleExpiry,ReagentKit,ReagentKitPartID,ReagentKitExpiry)
                VALUES (""" + str(s_placeholders) +")" #%s is the placeholder for a string
        self.cursor.executemany(sqlcommand, [new_datalist])
        self.db.commit() 

        #Retrieve the ReadID from the Rds table to populate the Linking table
        #Open up the class (initialise it with the correct data for each different piece of information)
        rd_lst = []
        link_msr_rds = self.link.PopLinker(self.username,self.password)
        #rd_lst.append(link_msr_rds.populateTable(reads_list[0],reads_list[1],reads_list[2]))
        for i in xrange(0,len(reads_list),num_entries_rds_tbl):
            reads_input = reads_list[i:(i+num_entries_rds_tbl)]
            #print reads_input
            rd_lst.append(run_id)
            rd_lst.append(link_msr_rds.populateTable(reads_input[0],reads_input[1],reads_input[2])) #Fixed for 3 entries here
        
        get_num_lnk_rds = ('(%s,%s),' * read_num).rstrip(',') #Known 2 entries for linker table and then strip trailing comma 

        #datalist = [run_id,cond2,run_id,cond22,run_id,cond223,run_id,4]
        rd_link_lst = rd_lst

        #Link the MiSeqRun and the Rds tables- THIS NEEDS FINISHING
        sqlcommand = """ INSERT IGNORE INTO LinkMiSeqRunRds
                    (MiSeqRunID, ReadID)
                    VALUES """ + str(get_num_lnk_rds)
        #print sqlcommand

        self.cursor.executemany(sqlcommand, [rd_link_lst])

        self.db.commit() #This line has to be there or the changes don't happen!! Could also put db.autocommit(True) at the beginning
        self.db.close()

        #print "Insert happened check"
        
