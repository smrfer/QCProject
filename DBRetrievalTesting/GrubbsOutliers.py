#Source https://github.com/choderalab/cadd-grc-2013/blob/master/notebooks/Outliers.ipynb

import numpy

def Grubbs_outlier_test(y_i, alpha=0.95):
    """
    Perform Grubbs' outlier test.
    
    ARGUMENTS
    y_i (list or numpy array) - dataset
    alpha (float) - significance cutoff for test

    RETURNS
    G_i (list) - Grubbs G statistic for each member of the dataset
    Gtest (float) - rejection cutoff; hypothesis that no outliers exist if G_i.max() > Gtest
    no_outliers (bool) - boolean indicating whether there are no outliers at specified significance level
    index (int) - integer index of outlier with maximum G_i 
    #t comes from the upper critical value of the t-distribution with N-2 degrees of freedom and a significance level of alpha/2N  
    """
    s = y_i.std()
    G_i = numpy.abs(y_i - y_i.mean()) / s
    N = y_i.size
    from scipy import stats
    t = stats.t.isf(1 - alpha/(2*N), N-2) 
    Gtest = (N-1)/numpy.sqrt(N) * numpy.sqrt(t**2 / (N-2+t**2))    
    G = G_i.max()
    index = G_i.argmax()
    no_outliers = (G > Gtest)
    return [G_i, Gtest, no_outliers, index]

def Grubbs_outlier_cutoff_distribution(N):
    """
    Generate the Grubbs' outlier test statistic cutoff distribution for various values of significance.
    """
    npoints = 50
    alphas = logspace(0, -20, npoints)
    from scipy import stats
    Gtest = numpy.zeros([npoints], numpy.float64)
    for (i,alpha) in enumerate(alphas):
        t = stats.t.isf(1 - alpha/(2*N), N-2)
        Gtest[i] = (N-1)/numpy.sqrt(N) * numpy.sqrt(t**2 / (N-2+t**2));  
    return [alphas, Gtest]