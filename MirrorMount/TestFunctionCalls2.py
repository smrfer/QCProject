'''
Created on 17 Mar 2016

@author: Admin
'''
import ReadMeans as RdM
import numpy as np
import matplotlib.pyplot as pl

import ReadModelling as RM

model = RM.ReadModelling()

num_cycles = 75 #For testing only

#For a greater range of options regarding cycle number
#create_x = np.arange(50,300) # Modify this according to need
start_x = 50
stop_x = 300

polynomial_order = 5
std_threshold_set = 2

read_means = RdM.ReadMeans()
print read_means.returnThresholdGrad(start_x,stop_x,"r1",polynomial_order,std_threshold_set,num_cycles)
print read_means.returnThresholdGrad(start_x,stop_x,"r2",polynomial_order,std_threshold_set,num_cycles)

#Not working right. Working better now. -0.05 are initial parameter guesses.
model_function_r1 = model.fitExp(read_means.returnMeanX(),read_means.returnMeanY_r1(read_means.returnMeanX()),-0.05,-0.05,-0.05)
test_model_exp_vals_r1 = (model_function_r1[0] * np.exp(-model_function_r1[1] * (np.arange(start_x,stop_x))) + model_function_r1[2])

pl.figure(1)
pl.plot((np.arange(start_x,stop_x)),test_model_exp_vals_r1)
pl.show()