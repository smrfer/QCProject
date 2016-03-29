'''
Created on 17 Mar 2016

@author: Admin
'''
import ReadModelling as RM
import numpy as np
import matplotlib.pyplot as pl

means_dict_r1 = {'75':-0.000525027,'131':-0.000564013,'151':-0.000907303,'200':-0.00201205,'250':-0.001703451,'251':-0.00191669,'300':-0.003515287}
means_dict_r2 = {'75':-0.000516316,'131':-0.000591712,'151':-0.001066129,'200':-0.002524631,'250':-0.00331588,'251':-0.002847048,'300':-0.004229047}
std_dict_r1 = {'75':0.000245543,'151':0.000786794,'200':0.00077823,'251':0.000685924} #Incomplete- removed where only a few data points
std_dict_r2 = {'75':0.000748647,'151':0.000757766,'200':0.000757766,'251':0.000803875} #Incomplete- removed where only a few data points

#Work on getting this information from the dictionary
#List of keys
means_x = means_dict_r1.keys()
means_x = [int(i) for i in means_x]
means_x.sort()
np_means_x = np.asarray(means_x)

#Data for r1
means_y_r1 = [means_dict_r1.get(str(key),None) for key in means_x]
np_means_y_r1 = np.asarray(means_y_r1)

#Data for r2
means_y_r2 = [means_dict_r2.get(str(key),None) for key in means_x]
np_means_y_r2 = np.asarray(means_y_r2)
#Put in exception handling here in case r1 has no r2


#make the models for the two reads- comes from the average of all available runs of that cycle number
model = RM.ReadModelling()
#read 1
model_function_r1 = model.fitPolynom(np_means_x,np_means_y_r1,5)

#ADDTIONAL MODEL- exponential
test_model_exp_r1 = model.fitExp(np_means_x,np_means_y_r1,-0.05,-0.05,-0.05)




#read 2
model_function_r2 = model.fitPolynom(np_means_x,np_means_y_r2,5)

#ADDTIONAL MODEL- exponential -0.05 are initial parameter guesses
test_model_exp_r2 = model.fitExp(np_means_x,np_means_y_r2,-0.05,-0.05,-0.05)

#For a greater range of options regarding cycle number
create_x = np.arange(50,300) # Modify this according to need

#EXTRA MODEL WORKING
test_model_exp_vals_r1 = (test_model_exp_r1[0] * np.exp(-test_model_exp_r1[1] * create_x) + test_model_exp_r1[2])
test_model_exp_vals_r2 = (test_model_exp_r2[0] * np.exp(-test_model_exp_r2[1] * create_x) + test_model_exp_r2[2])


#Work out the correct std dev to apply
#Set threshold
std_threshold = 2

#List of available values
stds_x = std_dict_r1.keys()
stds_x = [int(i) for i in stds_x]
stds_x.sort()
np_stds_x = np.asarray(stds_x)

#Old method to get std devs
np_std_list_r1 = model.getStdsArrMethod1(stds_x,create_x,std_dict_r1)
np_std_list_r2 = model.getStdsArrMethod1(stds_x,create_x,std_dict_r2)


#Stds Data for r1
stds_y_r1 = [std_dict_r1.get(str(key),None) for key in stds_x]
np_stds_y_r1 = np.asarray(stds_y_r1)

#Stds Data for r2
stds_y_r2 = [std_dict_r2.get(str(key),None) for key in stds_x]
np_stds_y_r2 = np.asarray(stds_y_r2)

#New method to get std devs (linear)- can smooth it out- comment these out to compare
np_std_list_r1 = model.getStdsLinear(np_stds_x,np_stds_y_r1,create_x)
np_std_list_r2 = model.getStdsLinear(np_stds_x,np_stds_y_r2,create_x)

#New method to get std devs (interpolate)- comment these out to compare
np_std_list_r1 = model.getStdsLinInterp(np_stds_x,np_stds_y_r1,create_x)
np_std_list_r2 = model.getStdsLinInterp(np_stds_x,np_stds_y_r2,create_x)


low_r1 = model_function_r1(create_x) - (std_threshold * np_std_list_r1)
high_r1 = model_function_r1(create_x) + (std_threshold * np_std_list_r1)
low_r2 = model_function_r2(create_x) - (std_threshold * np_std_list_r2)
high_r2 = model_function_r2(create_x) + (std_threshold * np_std_list_r2)


#Plots to investigate the data
pl.figure(1)
pl.plot(create_x,model_function_r1(create_x))
pl.figure(2)
pl.plot(create_x,model_function_r1(create_x))
pl.plot(create_x,low_r1)
pl.plot(create_x,high_r1)
pl.figure(3)
pl.plot(create_x,model_function_r2(create_x))
pl.figure(4)
pl.plot(create_x,model_function_r2(create_x))
pl.plot(create_x,low_r2)
pl.plot(create_x,high_r2)
pl.figure(5)
pl.plot(means_x,means_y_r1)
pl.plot(create_x,model_function_r1(create_x))
pl.figure(6)
pl.plot(means_x,means_y_r2)
pl.plot(create_x,model_function_r2(create_x))
pl.figure(7)
pl.plot(means_x,means_y_r1)
pl.plot(create_x,test_model_exp_vals_r1)
pl.figure(8)
pl.plot(means_x,means_y_r2)
pl.plot(create_x,test_model_exp_vals_r2)

pl.show()
