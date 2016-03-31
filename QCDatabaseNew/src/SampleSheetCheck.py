'''
Created on 13 Nov 2015

@author: Sara
'''

class SampleSheetChk(object):
    '''
    Checks for the presence of a sample sheet. If there isn't one then errors.
    '''
    def __init__(self,filepath):
        import os
        self.os = os
        self.filepath = filepath
        
    def checkSS(self):
        ss = None
        for f in self.os.listdir(self.filepath):
            #print f
            if f.lower() == ('samplesheet.csv'):
                #print f
                ss = f
            elif f.lower() == ('samplesheetused.csv'): #Allow for cases where this has copied over as well/instead
                ss = f
        #print self.filepath
        #assert ss != None #If this is triggered, no SampleSheet file was found
        #print ss
        try:
            sample_sheet = self.filepath + ss
        except TypeError:
            sample_sheet = ss #There is no sample sheet and sample sheet is set to None type
        return sample_sheet