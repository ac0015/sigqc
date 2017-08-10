import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import csv
from sigqc import sigqc_asciitestcase
from sigqc import sigqc_unitdata
from sigqc import sigqc_pca
from sigqc import sigqc_report

#########################################################################################################################
# ImplementPCA.py
# Austin Coleman
#
# Script to implement Principal Component Analysis in the context of SigQC data.
# Takes a file exported from SigQC, performs Principal Component Analysis, and
# writes output to a SigQC report.
#
# Example Use:
#  reference_file = "[full path here]\\Selected Good Units-Env Order-Metrics.csv"
#  storeReferenceData(reference_file, input_type='ascii', o_path="[full path here]", o_name="ReferenceData.csv")
#  refresults = "[o_path]\\[o_name]"
#  myTestFilePath = "[path to test file data]\\[test file name]"
#  implementPCA(refresults, myTestFilePath, input_type="ascii", o_file="PCA_Results_My_Test_Data", generate_report=True)
#
##########################################################################################################################

def implementPCA(i_referencefile, i_testfile, input_type="ascii", o_file="PCA_Results", generate_report=True, n_pcs=10):
    '''
    Use a reference set of eigenvectors to generate Principal Component
    Scores for each test unit within a user-specified file. 
    
    Inputs
    ------
        i_referencefile - String containing path to output .csv file from storeReferenceData() method.
            Must contain the eigenvalues, eigenvectors, and average vector of the reference 
            dataset.
        i_testfile - String containing path to test file containing units with test case 
            values to be tested. It is crucial that the units are consistent through
            each test case, as test case features will all be stacked into
            one array with rows denoting units and columns denoting test case
            values for each features of that particular unit.
        i_type - (Optional) String specifying the file input type. Currently,
            the SigQC ASCII Test Case Files and SigQC Unit Data files are 
            supported as "ascii" and "unit" respectively. The type defaults to
            "ascii".
        o_file - (Optional) String specifying the full path and name of the output file(s).
            Defaults to "PCA_Results". Note: This naming convention is used for both the 
            generation of the SigQC Report and the PC Scores .csv file (i.e. the default
            output will be produced in the current folder with the names "PCA_Results.docx"
            and "PCA_Results.csv" respectively).
        generate_report - (Optional) Boolean describing whether or not to generate the 
            SigQC report file 
        n_pcs - (Optional) Number of Principal Components to be plotted.
            Default is the first 10 PCs.
    
    Outputs
    -------
        If generate_report is set to True, will create SigQC Report file named [o_file].docx 
            containing plots of the PC Scores and save it to the path specified in o_file.
        Spreadsheet containing PC Scores for each unit as a file named [o_file].csv
        and save it to the path specified in o_file.
        This method does not explicitly return anything.
    '''
    ##################
    # Assign dataset
    ##################
    if (input_type.lower() == "ascii"):
        # Get test units...
        dataobj = sigqc_asciitestcase.SigQCAsciiTestCaseFile(i_testfile)
        headers = dataobj.getHeaders()
        serialnumbers = dataobj.getMatrixAt(0).getSerialNumbers()
        dataset = np.array(dataobj.getMatrixDataAt(0))
        for i in range(1,dataobj.getTestCaseCount()):
            dataset = np.hstack((dataset,dataobj.getMatrixDataAt(i)))  
    elif (input_type.lower() == "unit"):
        dataobj = sigqc_unitdata.SigQCUnitDataFile(i_testfile)
        headers = dataobj.GetCaseNames()
        serialnumbers = dataobj.GetSerialNumbers()
        dataset = np.array(dataobj.GetCaseDataTable())
    else:
        raise Exception("Error: Please provide a valid input_type. Valid options include 'ascii' and 'unit'")
    
    #########################
    # Parse reference data
    #########################
    avgvec = None
    evals = None
    evecs = []
    with open(i_referencefile, 'r') as f:
        for row in f:
            if ("BEGINAVGVECTOR" in row):
                row = next(f)
                avgvec = np.array(row.split(','), dtype=float)
                while ("ENDAVGVECTOR" not in row):
                    row = next(f)
            if ("BEGINSTANDDEV" in row):
                row = next(f)
                stddev = np.array(row.split(','), dtype=float)
                while ("ENDSTANDDEV" not in row):
                    row = next(f)
            if ("ISCORRMATRIX" in row):
                row = next(f)
                corr_matrix = str(row)
                while ("ENDCORRMATRIX" not in row):
                    row = next(f)
            if ("BEGINEVALS" in row):
                row = next(f)
                evals = np.array(row.split(','), dtype=float)
                while ("ENDEVALS" not in row):
                    row = next(f)
            if ("BEGINEVECS" in row):
                row = next(f)
                while ("ENDEVECS" not in row):
                    evecs.append(np.array(row.split(','),dtype=float))
                    row = next(f)
                    
    ###################################
    # Run PCA and finish SigQC Report
    ###################################
    pcscores = np.zeros((dataset.shape))
    
    # Initialize list of PC scores for boxplots
    boxplotlist = []
            
    # Calculate PC Scores with reference dataset as eigenvectors
    if ('True' in corr_matrix):
        pcscores = np.dot((dataset-avgvec)/stddev, evecs)
    else:
        pcscores = np.dot((dataset-avgvec), evecs)
            
    if (generate_report):
        report = sigqc_report.SigQCReport() # Initialize report
        
        # Create figures
        oname = "PCScores"
        header = headers[0].getProdName()+" PC Scores"
        sigqc_pca.plotPCScores(pcscores, header, o_name=oname, n_pcs=n_pcs)

        # Add figures to a new section of SigQC Report
        figs = []
        for j in range(n_pcs):
            figs.append(oname+str(j)+"-"+str(j+1)+".png")
            boxplotlist.append(pcscores[:,j])
        figs.append("Boxplot.png")
        
        sigqc_pca.plotPCBoxPlots(boxplotlist)

        # Add serial numbers
        str_serials = " , "
        str_serials = str_serials.join(serialnumbers)

        report.addSection(header+": Principal Component Boxplot", "Unit(s) Tested: "+str_serials, i_figures=figs)

        report.writeReport(o_docname=o_file)
    
    #######################################
    # Create .csv file with PC Scores
    #######################################
    
    colnames = np.arange(1,len(pcscores[0,:])+1)
    colnames = np.hstack(('Serial Number', colnames))
    tmppcscores = np.hstack((np.array(serialnumbers).reshape(len(serialnumbers),1), pcscores))
    finalpc = np.vstack((np.array(colnames).reshape(1,len(colnames)), tmppcscores))
    with open(o_file+".csv", 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerows(finalpc)
    return


# In[6]:

def storeReferenceData(i_referencefile, input_type="ascii", opath="", oname="ReferenceData.csv", corr_matrix=False):
    '''
    This method takes a file filled with reference (good) units, parses it according to the user
    specified input type, computes the eigenvalues and eigenvectors of the system, computes the
    mean vector of the set, and stores this information in an optionally user specified path and
    file name.
    
    Inputs
    ------
        i_referencefile - String denoting the absolute path and name of the file filled with reference
            units.
        input_type - (Optional) String that describes the file's input type which changes how the 
            reference file is parsed. Currently supported options are "ascii" for a SigQC ASCII 
            Test Case file or "unit" for a SigQC Unit Data file. Defaults to "ascii".
        opath - (Optional) String describing the output file path. Defaults to the current directory.
        oname - (Optional) String describing the output file name. Defaults to "ReferenceData.csv".
        corr_matrix - (Optional) Boolean specifying whether to use correlation matrix in
            eigenvector calculation instead of the covariance matrix. Defaults to false.
        
    Outputs
    -------
        Saves a .csv file containing the eigenvalues, eigenvectors, and mean vector of the system within
        the reference file. Output will be saved using the conventions specified with the opath and oname
        parameters.
        This method does not explicitly return anything.
    '''
    # Parse according to file type
    if (input_type.lower() == "ascii"):
        dataobj = sigqc_asciitestcase.SigQCAsciiTestCaseFile(i_referencefile)
        dataset = np.array(dataobj.getMatrixDataAt(0))
        for i in range(1,dataobj.getTestCaseCount()):
            dataset = np.hstack((dataset, dataobj.getMatrixDataAt(i)))
        avgvector = np.mean(dataset, axis=0)
        stddev = np.std(dataset, axis=0)
    elif (input_type.lower() == "unit"):
        dataobj = sigqc_unitdata.SigQCUnitDataFile(i_referencefile)
        dataset = np.array(dataobj.GetCaseDataTable())
        avgvector = np.mean(dataset, axis=0)
        stddev = np.std(dataset, axis=0)
    else:
        raise Exception("Error: Please provide a valid input_type. Valid options include 'ascii' and 'unit'")
    
    # Calculate eigenvalues and eigenvectors on covariance (or correlation) matrix
    cov_matrix = sigqc_pca.getCovariance(dataset, center_around_mean=True, scale_by_nrows=True, corr_matrix=corr_matrix) 
    evals, evecs = sigqc_pca.getEigen(cov_matrix)
    
    # Store eigenvalues, eigenvectors, and average vector
    with open(opath+oname, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(["BEGINAVGVECTOR"])
        writer.writerow(avgvector)
        writer.writerow(["ENDAVGVECTOR"])
        writer.writerow(["BEGINSTANDDEV"])
        writer.writerow(stddev)
        writer.writerow(["ENDSTANDDEV"])
        writer.writerow(["ISCORRMATRIX"])
        writer.writerow([str(corr_matrix)])
        writer.writerow(["ENDCORRMATRIX"])
        writer.writerow(["BEGINEVALS"])
        writer.writerow(evals)
        writer.writerow(["ENDEVALS"])
        writer.writerow(["BEGINEVECS"])
        writer.writerows(evecs)
        writer.writerow(["ENDEVECS"])
    return


# In[ ]:



