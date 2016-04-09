'''
Created on 31 Mar 2016

@author: Admin
'''
import MySQLdb
import sys

'''
A test to ensure that the data in the Sample Name field of the IndexMetricsMSR relation
is within an acceptable range of characters.
Potentially requires refinement to ensure that lab-based colleagues use only these conventions
in naming a sample.
'''

def retrieveData():
    #Connect to the database- user with select privileges only
    try:
        db = MySQLdb.connect("localhost",sys.argv[1],sys.argv[2], "ngsqc" ) #Pass username and password as command line arguments

    except:
        sys.exit("Enter correct username and password!")
        
    cursor = db.cursor()
    
    sql_command = """ SELECT SampleName
                        FROM IndexMetricsMSR """
    cursor.execute(sql_command)
    return cursor.fetchall()


def testSampleName(sample_names):
    #sample_names = [['15M06473','test-sample','AnotherS4aml3','control-sample_','sample*']]
    allowed_characters = ['1','2','3','4','5','6','7','8','9','0',
                        'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p',
                        'q','r','s','t','u','v','w','x','y','z',
                        '-','_','.','/',' '] #Note / and space added to handle an odd case
    #print sample_names
    for sample in sample_names:
        print sample[0]
        for letter in sample[0]:
            assert letter.lower() in allowed_characters
    return "Sample names OK"


print testSampleName(retrieveData())