'''
Created on 17 Mar 2016

@author: Admin
'''
class ReadMeans(object):
    
    def __init__(self):
        import ReadModelling as RM
        import numpy as np
        from scipy.optimize import curve_fit
        self.curve_fit = curve_fit
        self.RM = RM
        self.np =np
        #Global variables
        self.means_dict_r1 = {'75':-0.000525027,'131':-0.000564013,'151':-0.000907303,'200':-0.00201205,'250':-0.001703451,'251':-0.00191669,'300':-0.003515287}
        self.means_dict_r2 = {'75':-0.000516316,'131':-0.000591712,'151':-0.001066129,'200':-0.002524631,'250':-0.00331588,'251':-0.002847048,'300':-0.004229047}
        self.std_dict_r1 = {'75':0.000245543,'151':0.000786794,'200':0.00077823,'251':0.000685924} #Incomplete- removed where only a few data points
        self.std_dict_r2 = {'75':0.000748647,'151':0.000757766,'200':0.000757766,'251':0.000803875} #Incomplete- removed where only a few data points
        
    def returnMeanX(self):
        #List of keys
        means_x = self.means_dict_r1.keys()
        means_x = [int(i) for i in means_x]
        means_x.sort()
        return self.np.asarray(means_x)
    
    def returnMeanY_r1(self,x_vals):
        means_y = [self.means_dict_r1.get(str(key),None) for key in x_vals]
        return self.np.asarray(means_y)
    
    def returnMeanY_r2(self,x_vals):
        means_y = [self.means_dict_r2.get(str(key),None) for key in x_vals]
        return self.np.asarray(means_y)   
        
    def returnStdX(self):
        stds_x = self.std_dict_r1.keys()
        stds_x = [int(i) for i in stds_x]
        stds_x.sort()
        return self.np.asarray(stds_x)
    
    def returnStdY_r1(self,x_vals):
        stds_y = [self.std_dict_r1.get(str(key),None) for key in x_vals]
        return self.np.asarray(stds_y)
    
    def returnStdY_r2(self,x_vals):
        stds_y = [self.std_dict_r2.get(str(key),None) for key in x_vals]
        return self.np.asarray(stds_y) 
     
    def returnThresholdGrad(self,desired_range_1,desired_range_2,read,polynom_order,std_dev_threshold,num_cycles):
        desired_range = self.np.arange(desired_range_1,desired_range_2)
        if read == "r1":
            means_x = self.returnMeanX()
            means_y_r1 = self.returnMeanY_r1(means_x)
            model = self.RM.ReadModelling()
            #read 1
            model_function_r1 = model.fitPolynom(means_x,means_y_r1,polynom_order)
            #New method to get std devs (interpolate)
            std_x = self.returnStdX()
            np_std_list_r1 = model.getStdsLinInterp(std_x,self.returnStdY_r1(std_x),desired_range)
            #Stds Data
            low_r1 = model_function_r1(desired_range) - (std_dev_threshold * np_std_list_r1)
            return low_r1[(num_cycles-1-desired_range_1)] #Python is 0-indexed, and there's an offset of whatever is start of desired range to this array
        
        elif read == "r2":
            means_x = self.returnMeanX()
            means_y_r2 = self.returnMeanY_r2(means_x)
            model = self.RM.ReadModelling()
            #read 2
            model_function_r2 = model.fitPolynom(means_x,means_y_r2,polynom_order)
            #New method to get std devs (interpolate)
            std_x = self.returnStdX()
            np_std_list_r2 = model.getStdsLinInterp(std_x,self.returnStdY_r2(std_x),desired_range)
            #Stds Data
            low_r2 = model_function_r2(desired_range) - (std_dev_threshold * np_std_list_r2)
            return low_r2[(num_cycles-1-desired_range_1)] # Python is 0-indexed, and there's an offset of whatever is start of desired range to this array
        else:
            raise Exception("Incorrect read number specified, please enter r1 or r2 for this function input")
        
    def returnThresholdGrad2(self,desired_range_1,desired_range_2,read,std_dev_threshold,num_cycles):
        desired_range = self.np.arange(desired_range_1,desired_range_2)
        '''
        -0.05 are the best initial guesses for parameters now- fix so not hardcoded later
        '''
        if read == "r1":
            means_x = self.returnMeanX()
            means_y_r1 = self.returnMeanY_r1(means_x)
            model = self.RM.ReadModelling()
            #read 1
            model_function_r1 = model.fitExp(means_x,means_y_r1,-0.05,-0.05,-0.05)
            #New method to get std devs (interpolate)
            std_x = self.returnStdX()
            np_std_list_r1 = model.getStdsLinInterp(std_x,self.returnStdY_r1(std_x),desired_range)
            #Stds Data
            low_r1 = model_function_r1(desired_range) - (std_dev_threshold * np_std_list_r1)
            return low_r1[(num_cycles-1-desired_range_1)] #Python is 0-indexed, and there's an offset of whatever is start of desired range to this array
        
        elif read == "r2":
            means_x = self.returnMeanX()
            means_y_r2 = self.returnMeanY_r2(means_x)
            model = self.RM.ReadModelling()
            #read 2
            model_function_r2 = model.fitExp(means_x,means_y_r2,-0.05,-0.05,-0.05)
            #New method to get std devs (interpolate)
            std_x = self.returnStdX()
            np_std_list_r2 = model.getStdsLinInterp(std_x,self.returnStdY_r2(std_x),desired_range)
            #Stds Data
            low_r2 = model_function_r2(desired_range) - (std_dev_threshold * np_std_list_r2)
            return low_r2[(num_cycles-1-desired_range_1)] # Python is 0-indexed, and there's an offset of whatever is start of desired range to this array
        else:
            raise Exception("Incorrect read number specified, please enter r1 or r2 for this function input")    
        
        
    def linearFit(self,x_val,y_val,p1=-0.05,p2=-0.05):
        def linFunc(x, p1,p2):
            return (p1 * x + p2) #Linear
        #This requires a function as input
        optimal_vals, covar = self.curve_fit(linFunc,x_val,y_val, p0=(p1,p2))
        return optimal_vals
        
    def returnThresholdVals(self,desired_range_1,desired_range_2,read,polynom_order,std_dev_threshold,num_cycles):
        desired_range = self.np.arange(desired_range_1,desired_range_2)
        if read == "r1":
            means_x = self.returnMeanX()
            means_y_r1 = self.returnMeanY_r1(means_x)
            model = self.RM.ReadModelling()
            #read 1
            model_function_r1 = model.fitPolynom(means_x,means_y_r1,polynom_order)
            #New method to get std devs (interpolate)
            std_x = self.returnStdX()
            np_std_list_r1 = model.getStdsLinInterp(std_x,self.returnStdY_r1(std_x),desired_range)
            #Stds Data
            low_r1 = model_function_r1(desired_range) - (std_dev_threshold * np_std_list_r1)
            return low_r1
        
        elif read == "r2":
            means_x = self.returnMeanX()
            means_y_r2 = self.returnMeanY_r2(means_x)
            model = self.RM.ReadModelling()
            #read 2
            model_function_r2 = model.fitPolynom(means_x,means_y_r2,polynom_order)
            #New method to get std devs (interpolate)
            std_x = self.returnStdX()
            np_std_list_r2 = model.getStdsLinInterp(std_x,self.returnStdY_r2(std_x),desired_range)
            #Stds Data
            low_r2 = model_function_r2(desired_range) - (std_dev_threshold * np_std_list_r2)
            return low_r2
        else:
            raise Exception("Incorrect read number specified, please enter r1 or r2 for this function input")
    
    def returnThresholdVals2(self,desired_range_1,desired_range_2,read,polynom_order,std_dev_threshold,num_cycles):
        desired_range = self.np.arange(desired_range_1,desired_range_2)
        if read == "r1":
            means_x = self.returnMeanX()
            means_y_r1 = self.returnMeanY_r1(means_x)
            model = self.RM.ReadModelling()
            #read 1
            model_function_r1 = model.fitExp(means_x,means_y_r1,-0.05,-0.05,-0.05)
            #New method to get std devs (interpolate)
            std_x = self.returnStdX()
            np_std_list_r1 = model.getStdsLinInterp(std_x,self.returnStdY_r1(std_x),desired_range)
            #Stds Data
            low_r1 = model_function_r1(desired_range) - (std_dev_threshold * np_std_list_r1)
            return low_r1
        
        elif read == "r2":
            means_x = self.returnMeanX()
            means_y_r2 = self.returnMeanY_r2(means_x)
            model = self.RM.ReadModelling()
            #read 2
            model_function_r2 = model.fitExp(means_x,means_y_r2,-0.05,-0.05,-0.05)
            #New method to get std devs (interpolate)
            std_x = self.returnStdX()
            np_std_list_r2 = model.getStdsLinInterp(std_x,self.returnStdY_r2(std_x),desired_range)
            #Stds Data
            low_r2 = model_function_r2(desired_range) - (std_dev_threshold * np_std_list_r2)
            return low_r2
        else:
            raise Exception("Incorrect read number specified, please enter r1 or r2 for this function input")    
           
    