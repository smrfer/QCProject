'''
Created on 27 Nov 2015

@author: Sara
'''
class SupplementaryTools(object):
    def __init__(self):
        import numpy as np
        self.np = np
             
    def locTileNo(self,inp_column):
        count = 0
        for index,cycle_number in enumerate(inp_column): #In list of cycle numbers
            if cycle_number != 1 and count < 1:
                count += 1
                return index
    
    def findCycleNos(self,inp_column,num_tiles):
        cycle = []
        for i in xrange(0,len(inp_column),num_tiles):
            cycle.append(inp_column[i])
        return cycle
    
    def findMeans(self,inp_arr,inp_column,num_tiles,column=2):
        means = []
        for i in xrange(0,len(inp_column),num_tiles):
            section = []
            for j in inp_arr[(i):(i+num_tiles),column]:
                section.append(j)
            mn = self.np.mean(section)
            #print inp_arr[i,1]
            means.append(mn)
        return means
    
    def findMedians(self,inp_arr,inp_column,num_tiles,column=2):
        meds = []
        for i in xrange(0,len(inp_column),num_tiles):
            section = []
            for j in inp_arr[(i):(i+num_tiles),column]:
                section.append(j)
            md = self.np.median(section)
            #print inp_arr[i,1]
            meds.append(md)
        return meds
    
    def findStdDev(self,inp_arr,inp_column,num_tiles,column=2):
        stdev = []
        for i in xrange(0,len(inp_column),num_tiles):
            section = []
            for j in inp_arr[(i):(i+num_tiles),column]:
                section.append(j)
            sd = self.np.std(section) #Set optional parameter ddof (delta degrees of freedom) to 1 to get same result as Matlab
            #print inp_arr[i,1]
            stdev.append(sd)
        return stdev
    
    def findIqr(self,inp_arr,inp_column,num_tiles,column=2):
        iqr_l = []
        for i in xrange(0,len(inp_column),num_tiles):
            section = []
            for j in inp_arr[(i):(i+num_tiles),column]:
                section.append(j)
            q75 = self.np.percentile(section, 75, interpolation='higher')
            #print q75
            q25 = self.np.percentile(section, 25, interpolation='lower')
            #print q25
            iqr = q75 - q25
            #print iqr
            iqr_l.append(iqr)
        return iqr_l
    
    def getXArray(self,array_num_values,num_x_per_y):
        x = []
        for elem in array_num_values:
            #print elem
            #print str(elem)*num_x
            for i in xrange(num_x_per_y):
                #print i
                x.append(elem)
        return x
    
    def getNormIntOverCycle(self,array,array_column,number_tiles,col_no):
        ans = []
        for i in xrange(0,len(array_column),number_tiles):
            lst = []
            #print i
            for j in array[(i):(i+number_tiles),col_no]:
                #print j
                lst.append(j)
            maxim = max(lst)
            for k in lst:
                ans.append(float(k)/float(maxim))
        return self.np.asarray(ans)
    
    def findSamplesPerRun(self,array_num_reads_per_sample,miseqid_col):
        '''
        Returns the number of reads per sample against the MiSeq identifier
        Takes in the data extract from Index Metrics, with MiSeqRunID, SampleName and NumberOfClusters
        '''
        #This is missing the last entry- fixed with the identify last iteration through loop
        num_reads_sample = []
        for i,v in enumerate(array_num_reads_per_sample[:,miseqid_col]):
            #print "Working"
            if i == (len(array_num_reads_per_sample[:,miseqid_col])-1):
                num_reads_sample.append((i+1) - prev_i)
            if v != array_num_reads_per_sample[:,miseqid_col][i-1]:
                if i == 0:
                    prev_i = i
                else:
                    num_reads_sample.append(i - prev_i)
                    prev_i = i
        return num_reads_sample
        
    def outputRunReadsPerSample(self,reads_per_sample,reads_per_run,num_col):
        '''
        Outputs the number of samples per run adjacent to the number of samples
        Useful for performing array division to get the proportion of samples per run
        '''    
        storage_lst = []
        for sample_entry in reads_per_sample[:,0]:
            for run_i,run_entry in enumerate(reads_per_run[:,0]):
                if sample_entry == run_entry:
                    storage_lst.append(reads_per_run[run_i,num_col])
        return self.np.asarray(storage_lst)
    
    def pullSection(self,inp_arr,n_per_sample_list):
        '''
        Unfinished
        '''
        prev_n = 0
        for n in n_per_sample_list:
            print n
            print inp_arr[prev_n:prev_n + n]
            prev_n += n
        
        