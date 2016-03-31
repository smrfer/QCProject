'''
Created on 12 Nov 2015

@author: Sara
'''
class IDRunParams(object):
    '''
    Finds out what the run parameters case is and returns that to the calling script.
    '''
    def __init__(self,filepath):
        import os
        self.os = os
        self.filepath = filepath
        
        
    def checkRP(self):
        run_p = None
        for f in self.os.listdir(self.filepath):
            #print f
            if f.lower() == ('runparameters.xml'):
                #print f
                run_p = f
        #print self.filepath
        assert run_p != None #If this is triggered, no runparameters file was found
        return self.filepath + run_p
        