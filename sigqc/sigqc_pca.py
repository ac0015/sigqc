import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from sigqc import sigqc_primitives
import os
import csv
import matplotlib.cm 

#####################################################################################################################################
# sigqc_pca.py
# Austin Coleman
#
# Traditional principal component analysis module.
#
# Example Usage:
#  basepath = "[your path here]\\"
#  plotpath = basepath + "Distributions\\"
#
#  if ( os.path.exists(plotpath) == False ):
#      os.mkdir(plotpath)
#
#  casedata = np.array(np.loadtxt(basepath + "[your data].csv" , delimiter=',', skiprows=2, usecols=range(3,30)),dtype=float)
#  cov_matrix = getCovariance(casedata)
#  e_vals, e_vects = getEigen(cov_matrix)
#  e_vals, e_vects = sortEigen(e_vals, e_vects)
#  pc = sigqc_pca.getPCScores(casedata, e_vals, e_vects)
#
#  plotPCScores(pc,n_pcs=4)
#  plotCumPropVar(pc,n_pcs=6,path=plotpath+"CumulativeProportionVar")
#
#####################################################################################################################################

def getCovariance(i_dataset, corr_matrix=False, scale_by_nrows=True, center_around_mean=True):
    ''' 
    Returns the covariance matrix (or correlation matrix if specified) of the dataset as a numpy array
        
    Inputs
    ------
        i_dataset - Array type which contains the dataset.
        corr_matrix - (Optional) Boolean specifying whether to use the correlation
            matrix instead of the covariance matrix. Defaults to false.
        scale_by_nrows - (Optional) Boolean that tells the method whether
            or not to divide by the number of rows in the original dataset.
            Defaults to true, should be set to false when getting the
            covariance matrix from a row vector.
        center_around_mean - (Optional) Boolean that tells the method
            whether to subtract the means from the dataset to standardize
            them. Defaults to true.

    Outputs
    -------
        Returns a 2D numpy array containing the covariance matrix of the
        dataset. Unless changed with optional parameters, this matrix
        will be scaled by the number of rows and centered around the mean.
    '''    
    if (center_around_mean):
        means = np.array(np.mean(i_dataset,axis=0)).reshape((1,len(i_dataset[0,:])))
        ones = np.ones((len(i_dataset[:,0]),1))
        means_prime = np.dot(ones, means)
        a = i_dataset - means_prime

        # If correlation matrix is preferred, divide by standard dev.
        if (corr_matrix):
            std = np.std(a ,axis=0)
            a = a/std
    else:
        a = i_dataset
        
    dotresult = np.dot(a.T,a)
    
    if (scale_by_nrows):
        cov_matrix = dotresult/(len(i_dataset[:,0])-1)
    else:
        cov_matrix = dotresult
    return cov_matrix

def getEigen(i_array):
    '''
    Calculates the eigenvalues and eigenvectors in descending order
    as 1D and 2D arrays, respectively.

    Inputs
    ------
        i_array - Array type that contains the original dataset of a numeric type or the 
        variance-covariance matrix of original dataset.


    Outputs
    -------
        Returns the sorted (in descending order) eigenvalues as a 1D numpy array and
        the corresponding eigenvectors as a 2D numpy array. They are returned together
        respectively within a tuple.
    '''
    evals, evecs = np.linalg.eigh(i_array, UPLO='U')
    eigen = sortEigen(evals, evecs)

    return eigen

def sortEigen(i_evals, i_evects):
    '''
    Sorts eigenvalues and associated eigenvectors from highest to lowest.
    Returns eigenvalues and eigenvectors as 1D and 2D arrays respectively.

    Inputs
    ------
        i_evals - Eigenvalues to be sorted
        i_evects - Eigenvectors to be sorted
    '''
    indeces = i_evals.argsort()[::-1]   
    eigenvalues = i_evals[indeces]
    eigenvectors = i_evects[:,indeces] 
    return eigenvalues, eigenvectors

def getPCScores(i_dataset, i_evals, i_evects, n_pcs=None):
    '''
    Calculates and returns principal component scores for each unit in the 
    dataset as a 2D numpy array. 

    Inputs
    ------
        i_dataset - Array-like of numeric data type that contains original dataset
        i_evals - Eigenvalues from i_dataset
        i_evects - Associated eigenvectors with i_evals
        n_pcs - (Optional) Number of principal components to be calculate PC Scores
            with. Will default to using all PCs in calculation.

    Outputs
    -------
        Returns principal component scores for each unit in the dataset
        as a 2D numpy array. Rows denote indeces for dataset units. 
        Columns denote PC scores associated with those units.
    '''
    # If unspecified, use all PCs.
    if n_pcs == None:
        n_pcs = len(i_evects[0,:])+1

    pc_scores = np.zeros((n_pcs,len(i_dataset[:,0])))
    means = np.array(np.mean(i_dataset,axis=0)).reshape((1,len(i_dataset[0,:])))
    ones = np.ones((len(i_dataset[:,0]),1))
    means_prime = np.dot(ones, means)
    a = i_dataset - means_prime
    pc_scores = np.dot(a,i_evects)

    return pc_scores

def getTotalVariance(i_array):
    '''
    Calculates and returns the total variance of the dataset.

    Inputs
    ------
        i_array - Array-like that contains the original dataset of a numeric type or the 
        variance-covariance matrix of original dataset.

        Note: Failing to pass an array with a numeric dtype will raise a "unfunc isFinite" error.

    Outputs
    -------
        Returns the total variance of a dataset as a float.
    '''
    isCovMatrix = False
    variance = None

    if len(i_array[:,0]) == len(i_array[0,:]):
        for i in range(len(i_array[:,0])):
            for j in range(len(i_array[0,:])):
                if i_array[i,j] != i_array[j,i]:
                    break
                else:
                    isCovMatrix = True
    if isCovMatrix:
        variance = sum(i_array.diagonal())
    else:
        cov = getCovariance(i_array)
        variance = sum(cov.diagonal())
    return variance

def getCumPropVar(i_dataset, i_evals, i_evects, n_pcs=None):
    '''
    Calculates and returns the cumulative proportion of variance explained
    by the first n principal components.

    Inputs
    ------
        i_dataset - Array-like of numeric data type to calculate PC scores with
        i_evals - Eigenvalues from i_dataset
        i_evects - Associated eigenvectors with i_evals
        n_pcs - (Optional) Number of principle components to be used in PC score
            calculation. If none specified, all PCs are included. 

    Outputs
    -------
        Returns the cumulative proportion of variance explained by the first n
        principal components. Defaults to all principal components if n_pcs is
        not set by the user, in which case the the function should return 1.0 if
        traditional PCA is being used (that is - all of the variance should be
        explained by the set of PCs for the dataset).
    '''
    if n_pcs == None:
        n_pcs = len(i_evects[0,:])
    tot_var = getTotalVariance(i_dataset)
    cumu_prop = 0
    for val in i_evals[:n_pcs]:
        cumu_prop += val/tot_var
    return cumu_prop

def plotPCScores(i_pcscores, i_header=None, o_path="", o_name="PCScores", n_pcs=2):
    '''
    Plots matplotlib.pyplot objects (figures) depicting
    the principal component scores for the number of principal
    components specified.

    Inputs
    ------
        i_pcscores - Array-like of PC scores for each unit within a dataset
        i_header - (Optional) Header to use as plot title
        o_path - (Optional) String for output path (defaults to current folder)
        o_name - (Optional) String for filename (will add PC numbers valid for
            onto end of filename).
        n_pcs - (Optional) Number of PCs to plot. (i.e. n_pcs=3 will
            plot two figures, one displaying PC scores using PCs 1 and 2
            as axes, and another figure displaying PC scores using
            PCs 2 and 3 as axes). If none specified, will plot the first
            two PCs as axes.

    Outputs
    -------
        Saves plots of principal component scores using o_path as the base path
        to store all figures.
        Does not explicitly return anything.
    '''
    for i in range(n_pcs):
        plt.figure(i, figsize=(6,4))
        plt.grid()
        plt.scatter(i_pcscores[:,i],i_pcscores[:,i+1], edgecolor="black", alpha=0.6)
        plt.xlabel("PC"+str(i+1))
        plt.ylabel("PC"+str(i+2))
        plt.title(i_header)
        plt.legend()
        plt.savefig(o_path+o_name+str(i)+"-"+str(i+1))
    return

def plotCumPropVar(i_dataset, i_evals, i_evects, o_path="", o_name="VarianceExplained", n_pcs=2, col="green"):
    '''
    Calculates and plots the cumulative proportion of variance explained
    by the first n principal components.

    Inputs
    ------
        i_dataset - Array-like of numeric data type to calculate PC scores with
        i_evals - Eigenvalues from i_dataset
        i_evects - Associated eigenvectors with i_evals
        o_path - (Optional) String for output path (defaults to current folder)
        o_name - (Optional) String for filename
        n_pcs - (Optional) Number of principle components to be used in PC score
            calculation. If none specified, all PCs are included.
        col - (Optional) String denoting the bar graph color. Will be green
            if none specified.

    Outputs
    -------
        Saves a bar graph of the cumulative proportion of variance explained by
        the first n_pcs using o_path as the file path and o_name as the file name.
        Does not explicitly return anything.
    '''

    pc_prop = np.zeros((n_pcs))
    for j in range(1,n_pcs+1):
        pc_prop[j-1] = getCumPropVar(i_dataset,i_evals,i_evects,n_pcs=j)

    xlabs = []
    for i in range(1,n_pcs+1):
        xlabs.append('PC'+str(i))
    
    plt.figure(1)
    plt.bar(list(range(1,n_pcs+1)),pc_prop,color=col)
    plt.xticks(range(1,n_pcs+1,1),xlabs,size=8.0)
    plt.yticks(size=8.0)
    plt.ylabel("Proportion of Total Variance",size=8.0)
    plt.title("Cumulative Proportion of Variance Explained by Principal Components",size=10)
    plt.savefig(o_path+o_name)
    return

def plotPCBoxPlots(i_pcscores_T, o_path="", o_name="Boxplot"):
    '''
    Create, save and show boxplots of PC scores for each PCs stacked
    through the y axis.

    Inputs
    ------
        i_pcscores_T - The transpose of the PC score data. Rows
            should describe each individual PC with columns
            corresponding to each unit.
        o_path - (Optional) String for output path (defaults to current folder)
        o_name - (Optional) String for filename
    Outputs
    -------
        Saves the boxplot of Principal Components in 'o_path' saved as 'o_name'.
        Does not return anything explicitly.
    '''
    fig = plt.figure()
    plt.grid()
    plt.boxplot(i_pcscores_T, 0, 'bD', 0)
    plt.ylabel("PC")
    plt.xlabel("PC Score")
    plt.title("Boxplot of PC Scores")
    plt.savefig(o_path+o_name)
    return
