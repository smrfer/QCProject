'''
Created on 29 Feb 2016

@author: Admin
'''

import sys
import random

#Load in list of Runs
outpath = sys.path[0]
infile = outpath + "\\runs.txt"
#file_of_runs = open(infile, 'r')

#Create a list of runs for initial QC testing
outfilepath = outpath + "\\testruns.txt"
outfile = open(outfilepath, 'w')

#Create a list of runs for second lot of QC testing
outfilepath2 = outpath + "\\keepruns.txt"
outfile2 = open(outfilepath2, 'w')

with open(infile, 'r') as inf:
    runs = [element.rstrip('\n') for element in inf.readlines()]
#print runs

#Remove known a priori incomplete runs
runs.remove('130405_M00766_0006_000000000-A3FNU')
runs.remove('130918_M00766_0051_000000000-A5BDM')
runs.remove('131031_M00766_0061_000000000-A5M27')
runs.remove('140314_M00766_0027_000000000-A7C5E')
#Remove run from instrument that is not one of ours (unknown where it came from)
runs.remove('141027_M00749_0198_000000000-ABU2A')

#Divide the set into 2, one for test and one to keep
num_test = (len(runs)/2)

#Testset
testset = random.sample(runs,num_test)
for testrun in testset:
    outfile.write("%s\n" % testrun)
outfile.close()

#Keepset- using a list comprehension
keepset = [rn for rn in runs if rn not in testset]
for keeprun in keepset:
    outfile2.write("%s\n" % keeprun)
outfile2.close()

print "Runs randomly assigned to two test sets"   
    
    

    