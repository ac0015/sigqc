import numpy as np
from sigqc import sigqc_pca

####################################################################
# sigqc_hmethod.py
# Austin Coleman
#
# A script developed to implement the H Method - a modification
# of Principal Component Analysis that compares summations of 
# eigenvectors derived from their respective covariance matrices. 
# The hope is that the H Method acts as a pass/fail metric on 
# parts for the SigQC user.
#
# 8/2/2017
# Currently, this method does not show significant promise as a
# metric due to the fact that angles are very sensitive
# to the number of dimensions in the eigenvector set and only
# return an angle of zero degrees when the total eigenvectors
# match exactly. This issue may be investigated further to
# determine whether a different variation of the H Method
# may be more useful in realizing a pass/fail metric for the
# end user.
####################################################################

def hMethod(i_test_data, i_ref_data, angle_units="d"):
    '''
    Calculates the angles between the eigenvector of a single unit feature vector  (test unit)
    and a single feature vector (reference unit). The covariance matrices of the feature vectors are used 
    to calculate the eigenvectors, which are then summed and normalized to create a total eigenvector for 
    both the test and reference feature vectors. These total eigenvectors are then used to compute the
    angles between them.
    
    Inputs
    ------
        i_test_data - A 2D numeric array-like containing the magnitudes of the test feature vector. MUST be 2D.
        i_ref_data - A 2D numeric array-like containing the magnitudes of the referece feature vector. MUST be 2D.
        angle_units - (Optional) Defaults to degrees for the angle output. Accepts "d" for degrees or "r" for radians.
    
    Outputs
    -------
        Returns the angle between the two input total eigenvectors in the units specified with the
        angle_units parameter.
    '''
    # Calculate covariance matrices for the test and reference feature vectors. In our case, the covariance matrix is simply
    # the dot product of the transpose of the fest feature vector and itself. It will not be scaled by number of rows
    # or centered around the mean (i.e. calculation is simply A.Transpose dot A)
    test_data_cov = sigqc_pca.getCovariance(i_dataset=i_test_data, scale_by_nrows=False, center_around_mean=False)
    ref_data_cov = sigqc_pca.getCovariance(i_dataset=i_ref_data, scale_by_nrows=False, center_around_mean=False)
    
    # Calculate eigenvectors from covariance matrices
    test_evals, test_evecs = np.linalg.eigh(test_data_cov, UPLO='U')
    ref_evals, ref_evecs = np.linalg.eigh(ref_data_cov, UPLO='U')
    for i in range(len(test_evecs[0,:])):
        test_evecs[:,i] = test_evecs[:,i]*test_evals[i]
        ref_evecs[:,i] = ref_evecs[:,i]*ref_evals[i]
    
    # Sum to get total eigenvector for each matrix of eigenvectors
    total_test_evec = np.sum(test_evecs, axis=0)
    total_ref_evec = np.sum(ref_evecs, axis=0)
    
    # Normalize eigenvectors
    test_magnitude = calcMagnitude(total_test_evec)
    ref_magnitude = calcMagnitude(total_ref_evec)
    total_test_evec = total_test_evec/test_magnitude
    total_ref_evec = total_ref_evec/ref_magnitude
    
    # Calculate angle between eigenvectors
    return angleEvecs(total_test_evec, total_ref_evec, angle_units=angle_units)

def calcMagnitude(i_vector):
    '''
    Calculates the magnitude of a 1D numeric array-like and returns the magnitude
    as a float.
    '''
    return np.sqrt(sum(i_vector**2))

def angleEvecs(itot_test_eigenvec, itot_ref_eigenvec, angle_units="d"):
    '''
    Returns the angle between the total test eigenvector and
    total reference eigenvector.

    Inputs
    ------
        itot_test_eigenvec - The total (summed) eigenvector of the
            covariance matrix for a test unit
        itot_ref_eigenvec - The total (summed) eigenvector of the
            covariance matrix for a test unit
        angle_units - (Optional) The output units of the angle
            returned. Supported parameters are "d" for degrees or
            "r" for radians. Defaults to degrees.

    Outputs
    -------
        Returns the angle between the two input total eigenvectors
        in the units specified with the angle_units parameter.
    '''
    Q = np.dot(itot_ref_eigenvec.T, itot_test_eigenvec)
    angle = np.math.acos(Q)
    if (angle_units.lower() == "d"):
        angle = angle*(180/np.pi)
    elif (angle_units.lower() == "r"):
        angle = angle
    else:
        raise Exception("Units Error: Please use either angle_units='d' or angle_units='r' to specify degrees or radians respectively")
    return angle
