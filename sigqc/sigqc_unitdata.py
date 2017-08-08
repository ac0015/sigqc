import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from sigqc import sigqc_primitives

##################################################################################
# sigqc_unitdata.py
# Austin Coleman
#
# This module encompasses two classes, SigQCUnitDataFile, and SigQCUnitDataFiles
# which are needed to parse and encapsulate all the information contained within
# a SigQC Unit Data File exported from SigQC. Its usage should be mainly
# internal. This submodule relies on the sigqc_primitives submodule from
# the sigqc library.
#
# Example Usage:
#   fpath = "ascii test case file path\\"
#   fname = "ascii test case file name"
#   ascii_object = SigQCAsciiTestCaseFile(fpath+fname)
#   headers = ascii_object.getHeaders()
#
#   ### Many access methods for metadata from SigQCAsciiHeader objects ###
#   for header in headers:
#       product = header.getProdName()  
#       print(product)
#       test = header.getTestName()
#       print(test)
#
#   ### Handle test cases individually ###
#   first_matrix = ascii_object.getMatrixAt(0)
#   serial_numbers = first_matrix.getSerialNumbers()
#   domains = first_matrix.getXValues()
#   data = first_matrix.getYValues()
#
#   ### Handle all test cases at once ###
#   ### Only useful when all serial numbers are consistent ###
#   serialnumbers, domains, data, limits = ascii_object.getAllTestCases()
#
##################################################################################

###########################
# SigQCUnitDataFile Class
###########################
class SigQCUnitDataFile:
    '''
    The SigQCUnitDataFile class is designed to support reading of CSV files
    exported from SigQC using the "Unit Data Export" feature.  Standard use
    of this class is as follows:
    
        x = SigQCUnitDataFile()       
        x.SetFilename("D:\MyData\MyUnitDataFile.csv" )
        x.Read()
    
    '''      
    def __init__(self,i_filename=None,i_delimiter=","):
        '''
        Constructor for a SigQCUnitDataFile class to open and read the content of
        a specified unit data file.  If a filename is specified, then the file is
        read within this constructor and ready for query after construction.
        
        Input:
            i_filename - Specify the fully-qualified path to the unit data file
                         to be read.  The default value is None.  In that case, the
                         file must be read after construction.
                         
            i_delimiter- String that contains the delimiter character.  By default,
                         the delimiter is a comma.
                         
        Example:
            x = SigQCUnitDataFile("D:\MyData\MyUnitDataFile.csv", "\t")
            y = x.GetArray("1-GOPEN", "[GO] RL Start Click")
            
        OR
            x = SigQCUnitDataFile()
            x.SetFilename("D:\MyData\MyUnitDataFile.csv")
            x.SetDelimiter("\t")
            x.Read()
            y = x.GetArray("1-GOPEN", "[GO] RL Start Click")
        '''
        self._filename = i_filename
        self._delimiter = i_delimiter
        self._casedata = None
        self._serialnumbers = None
        self._dates = None
        self._times = None
        self._casenames = None
        self._testnames = None
        self._dataread = False
        if (self._filename is not None):
            self.Read()
        
    def SetFilename(self,i_filename):
        '''
        Set the fully qualified path to the unit data file to be read.
        
        '''
        self._filename = i_filename
        
    def SetDelimiter(self,i_delimiter):
        '''
        Set the delimiter to be used when parsing the targeted unit
        data file.
        
        Input:
            i_delimiter-  String that contains the delimiter character.  By default
                          on construction, the delimiter is a comma.
                        
        Example:
            x = SigQCUnitDataFile()       
            x.SetFilename("D:\MyData\MyUnitDataFile.csv" )
            x.SetDelimiter("\t") # Use the tab delimiter instead
            x.Read()
                    
        '''
        self._delimiter = i_delimiter
        
    def Read(self):
        '''
        Read the content of the targeted unit data file.
              
        Example:
            x = SigQCUnitDataFile()
            x.SetFilename("D:\MyData\MyUnitDataFile.csv" )
            x.Read()
            
        '''
        # Indicate that an attempt has been made to read the unit data file...
        self._dataread = True

        # Read the unit data file as text...
        textdata = np.genfromtxt(self._filename, dtype=str, comments=None, delimiter=self._delimiter, skip_header=0)
        if (textdata is None):
            return
        
        # Determine the number of rows and columns...
        cols = len(textdata[0,:])
        rows = len(textdata[:,0])
        
        # Split the serial numbers, date, time, test labels, case labels, and data columns...
        textlist = np.hsplit(textdata,(1,2,3,cols))
        self._serialnumbers = np.delete(textlist[0],(0,1) )
        valuestext = np.vsplit(textlist[3], (1,2,rows))
        self._testnames = valuestext[0].flatten()
        self._casenames = valuestext[1].flatten()
        self._casedata = valuestext[2]

        cols = len(self._casedata[0,:])
        rows = len(self._casedata[:,0])
        for i in range(0,rows):
            for j in range(0,cols):
                if (self._casedata[i,j] == "--------"):
                    self._casedata[i,j]="0.0"

        self._casedata = self._casedata.astype(np.float32)
            
    def GetSerialNumbers(self):
        '''
        Get an array of the serial numbers within the targeted unit data
        file.  Serial numbers are returned as a flat array of strings.
        
        '''
        return self._serialnumbers
    
    def GetCaseDataTable(self):
        '''
        Get a 2D array of all test case values within the targeted unit data
        file.  Each row of the data represents a set of measurements that are
        associated with a specific production unit serial number.  A column of
        the data represents values for a specific test case identified within
        the test case names.
        
        '''
        return self._casedata
    
    def GetCaseNames(self):
        '''
        Get an array of the test case names within the targeted unit data
        file.  Test case names are returned as a flat array of strings.
        They serve as the headers for columns of the data table.
        
        '''
        return self._casenames
    
    def GetTestCaseGroup(self):
        '''
        Get a SigQCTestCaseGroup that includes all of the test cases identified by
        the test and test case names within the data file.  The SigQCTestCaseGroup
        class is part of sigqc_primitives.
        
        Return:
            Instance of the SigQCTestCaseGroup class that manages the test case identifiers
            present within the unit data file.
        '''
        group = sigqc_primitives.SigQCTestCaseGroup()
        count = len(self._testnames)
        for i in range(0,count):
            group.AppendByNames("", self._testnames[i], self._casenames[i], True)
        return group
    
    def GetIndexOfCase(self, i_testname, i_casename):
        '''
        Get the column index relative to the start of the data table at which the
        given test case resides.  Test case uniqueness is guaranteed by both the
        acceptance test and test case names.
        
        Input:
            i_testname  - Specify the name of the acceptance test that contains
                          the targeted column values.
                        
        
            i_casename - String that specifies the test case name whose column
                         index is to be returned.
                   
        Return:
              'int' value that identifies the column index of the targeted
              test case.  Return -1 if the targeted column does not exist.
              
        Example:
            x = SigQCUnitDataFile()
            x.SetFilename("D:\MyData\MyUnitDataFile.csv" )
            x.Read()
            i = x.GetIndexOfCase("1-GOPEN", [GO] RL Start Click")
            
        '''
        indx = -1
        if ( self._casedata is not None ):
            cols = len(self._casedata[0,:])
            rows = len(self._casedata[:,0])
            for j in range(0,cols):
                if ((self._testnames[j] == i_testname) and (self._casenames[j] == i_casename)):
                    indx = j
                    break
        return indx
    
    def GetTestNames(self):
        '''
        Get the acceptance test names associated with each column of the
        data table.  Test names are returned as a flat array of strings.
        They serve as the headers for columns of the data table.

        '''
        return self._testnames
    
    def GetUniqueTestNames(self):
        '''
        Get the unique acceptance test names associated with the columns of
        the data table.  Unique test names are returned as a flat array of
        strings.

        '''
        uniquenames = []
        count = len(self._testnames)
        for i in range(0,count):
            if not (self._testnames[i] in uniquenames):
                uniquenames.append(self._testnames[i])
        return uniquenames
    
    def GetArray(self,i_testname,i_casename):
        '''
        Extract the columm of data values that are associated with the
        specified acceptance test and test case name.
        
        Input:
            i_testname  - Specify the name of the acceptance test that contains
                          the targeted column values.
                        
        
            i_casename - String that specifies the test case name whose column
                         index is to be returned.                      
                        
        Return:
            np.array(dtype=float64) of 1D that contains the requested
            data values.  'None' if the targeted test case values cannot
            be located.
            
        Example:
            x = SigQCUnitDataFile()
            x.SetFilename("D:\MyData\MyUnitDataFile.csv" )
            x.Read()
            casedata = x.GetArray("1-GOPEN", "[GO] RL Start Click")
            
        '''
        index = self.GetIndexOfCase(i_testname, i_casename)
        if ( index == -1):
            return None;
        return self._casedata[:,index]

    def HasBeenRead(self):
        '''
        Determine whether or not data has been read from the targeted unit
        data file.
        
        Return:
            If True, the targeted unit data file has been read, or an attempt
            has been made to read the data file at least once.  If False, no
            attempt has been made to read the data file.
        '''
        return self._dataread

#############################
# SigQCUnitDataFiles Class
#############################
class SigQCUnitDataFiles:
    '''
    The SigQCUnitDataFiles class is designed to manage multiple files and
    provide support for comparative studies such as station-to-station,
    model-to-model, and time-variant data studies.
    
    '''
    def __init__(self):
        self._files = []
        
    def AppendFile(self, i_datafile, i_delimiter=","):
        '''
        Append a file to the list of unit data files managed by the unit
        data file manager.
        
        Input:
            i_datafile - Specify a string that represents a fully qualified path
                         to a unit data file.  Optionally, you may supply an instance
                         of the SigQCUnitDataFile class.
                         
            i_delimiter- String that contains the delimiter character.  By default
                         on construction, the delimiter is a comma.  If the given
                         data file is an instance of the SigQCUnitDataFile, the
                         delimiter value is ignored.               
        
        Example:
            x = SigQCUnitDataFiles()
            x.AppendFile("D:\MyData\MyUnitDataFile_1.csv")
            x.AppendFile("D:\MyData\MyUnitDataFile_2.csv", "\t")
            x.AppendFile( SigQCUnitDataFile("D:\MyData\MyUnitDataFile_2.csv", "\t"))
            x.Read()
        '''
        if isinstance(i_datafile, SigQCUnitDataFile):
            self._files.append(i_datafile)
        elif isinstance(i_datafile, str):
            datafile = SigQCUnitDataFile()
            datafile.SetFilename(i_datafile)
            datafile.SetDelimiter(i_delimiter)
            self._files.append(datafile)
    
    def GetFileAt(self,i_index):
        '''
        Get the SigQCUnitDataFile at the specified index within the list of unit
        data files managed.
        
        Input:
            i_index - Specify the index of the unit data file to be retrieved.
            
        Return:
            Instance of the SigQCUnitDataFile class at the specified index within
            the list of managed data files.
            
        '''
        return self._files[i_index]
    
    def GetIndicesOfCase(self,i_testname,i_casename):
        '''
        Get the column indices relative to the start of the data table at which the
        given test case resides for each managed unit data file.  Test case uniqueness
        is guaranteed by both the acceptance test and test case names.
        
        Input:
            i_testname - Specify the name of the acceptance test that contains
                         the targeted column values.
        
        
            i_casename - String that specifies the test case name whose column
                         indices are to be returned.
        
        Return:
              'np.array(ndtype=int)' value that identifies the column indices of the targeted
              test case for each managed unit data file.  Files that do not contain the targeted
              test case will be represented by a -1 within the returned array.  If no files have
              been targeted, 'None' is returned.
              
        Example:
            x = SigQCUnitDataFiles()
            x.Append("D:\MyData\MyUnitDataFile_1.csv" )
            x.Append("D:\MyData\MyUnitDataFile_2.csv" )
            x.Append("D:\MyData\MyUnitDataFile_3.csv" )
            x.Read()
            i = x.GetIndexOfCase("1-GOPEN", [GO] RL Start Click")
            
        '''
        x = None
        count = len(self._files)
        if ( count > 0 ):
            x = np.zeros(count)
            for i in range(0,count):
                x[i] = self._files[i].GetIndexOfCase(i_testname, i_casename)
        return x
        
    def GetTestCaseGroup(self):
        '''
        Get a SigQCTestCaseGroup that includes all of the unique test cases identified by
        the test and test case names within all managed data files.  The SigQCTestCaseGroup
        class is part of sigqc_primitives.
        
        Return:
            Instance of the SigQCTestCaseGroup class that manages the test case identifiers
            present among all unit data files.
        '''
        group = sigqc_primitives.SigQCTestCaseGroup()
        count = len(self._files)
        if ( count > 0 ):
            for i in range(0,count):
                group.Append(self._files[i].GetTestCaseGroup())
        return group.MakeUniqueGroup()
        
    def Read(self):
        '''
        Read all of the unit data files managed that have not yet been read.
        
        Example:
            x = SigQCUnitDataFiles()
            x.AppendFile("D:\MyData\MyUnitDataFile_1.csv")
            x.AppendFile( SigQCUnitDataFile("D:\MyData\MyUnitDataFile_2.csv", "\t"))
            x.Read()
        '''
        for i in range(0,len(self._files)):
            if ( self._files[i].HasBeenRead() == False ):
                self._files[i].Read()
    
    def GetArrays(self, i_testname, i_casename):
        '''
        Get the all of the column data of the targeted test case found in all managed
        unit data files.
        
        Input:
            i_testname  - Specify the name of the acceptance test that contains
                          the targeted column values.
                        
        
            i_casename - String that specifies the test case name whose column
                         index is to be returned.                      
                        
        Return:
            Returns a list of 1D arrays of float values that contains the requested data
            values.  Each column (axis 1) of the result is a column of data associated with
            a single unit data file.  Returns an empty list if the targeted test case values
            cannot be located within any of the data files.
            
        Example:
            x = SigQCUnitDataFiles()
            x.AppendFile("D:\MyData\MyUnitDataFile_1.csv")
            x.AppendFile("D:\MyData\MyUnitDataFile_2.csv")
            x.AppendFile("D:\MyData\MyUnitDataFile_3.csv")
            x.Read()
            casedatalist = x.GetArrays("1-GOPEN", "[GO] RL Start Click")
        '''
        arraylist = []
        indices = self.GetIndicesOfCase(i_testname, i_casename)
        if (indices is not None):
            count = len(indices[:])
            for i in range(0,count):
                if (indices[i] >= 0):
                    x = self._files[i].GetArray(i_testname, i_casename)
                    if (x is not None):
                        arraylist.append(x)
        return arraylist
