'''
Created on 17 Mar 2016

@author: Admin
'''

class ReadModelling(object):
    '''
    Methods associated with fitting curves to data, as needed.
    '''
    def __init__(self):
        '''
        In this method initial values for the internal data are created. The instance variables.
        This is within the namespace of the class.
        '''
        import numpy as np
        self.np = np
        from scipy.optimize import curve_fit
        self.curve_fit = curve_fit
        
    def fitPolynom(self,x_vals,y_vals,polynom_order):
        '''
        Fits a polynomial to the data
        '''
        vals = self.np.polyfit(x_vals,y_vals,polynom_order)
        funct = self.np.poly1d(vals)
        return funct
    
    def fitExp(self,x_vals,y_vals,a,b,c):
        def funct(x, a, b, c):
            return (a * self.np.exp(-b * x) + c)
        popt, pcov = self.curve_fit(funct, x_vals, y_vals, p0=(a,b,c))
        return popt
    

    def getStdsArrMethod1(self,list_of_stds,range_of_values_required,dict_for_lookup):
        std_list_r1 = []
        for cyc_ind,cyc_no in enumerate(list_of_stds):  
            if cyc_ind == 0:   
                masking_array = (self.np.where(range_of_values_required <= list_of_stds[cyc_ind]))
                for i in xrange(len(masking_array[0])):
                    std_list_r1.append(dict_for_lookup.get(str(list_of_stds[cyc_ind]),"None")) 
            elif cyc_ind == (len(list_of_stds)-1):
                #Need to push this number on to the end  
                masking_array = (self.np.where((range_of_values_required > list_of_stds[(cyc_ind-1)])))
                for i in xrange(len(masking_array[0])):
                    std_list_r1.append(dict_for_lookup.get(str(list_of_stds[cyc_ind]),"None"))
            else:
                masking_array = (self.np.where((range_of_values_required <= list_of_stds[cyc_ind]) & (range_of_values_required > list_of_stds[(cyc_ind-1)])))
                for i in xrange(len(masking_array[0])):
                    std_list_r1.append(dict_for_lookup.get(str(list_of_stds[cyc_ind]),"None"))
        return self.np.asarray(std_list_r1)

    def getStdsLinear(self,x_val,y_val,desired_x_vals,p1=-0.05,p2=-0.05):
        def linFunc(x, p1,p2):
            return (p1 * x + p2) #Linear
        #This requires a function as input
        optimal_vals, covar = self.curve_fit(linFunc,x_val,y_val, p0=(p1,p2))
        linear_pred = ((optimal_vals[0] * desired_x_vals) + optimal_vals[1])
        return self.np.asarray(linear_pred)
    
    def getStdsLinInterp(self,x_val,y_val,desired_x_vals):
        return self.np.interp(desired_x_vals, x_val, y_val)
        
        
