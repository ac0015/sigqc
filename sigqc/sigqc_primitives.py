import numpy as np

class SigQCTestCaseID(object):
    '''
    The SigQCTestCaseID class is designed to uniquely identify a SigQC test case within the
    scope of a SigQC database.  SigQC defines a product data tree that is hierarchial
    in form - starting with a product model.  Product models serve as parents to acceptance
    tests.  Acceptance tests serve as parents to test cases.  SigQC preserves name uniqueness
    within each level of the hierarchy.  Thus, within a SigQC database, a test case is uniquely
    identified by its name, its parent acceptance test name, and the name of the product that
    owns the acceptance test.  An entire key to an acceptance test case can be represented by
    a period (".") delimited path of the form "product.test.case". 
    '''
    def __init__(self,i_productname="",i_testname="",i_casename="",i_exact=True):
        self._productname = i_productname
        self._testname = i_testname
        self._casename = i_casename
        self._exact = i_exact;
    
    def __str__(self):
        extension = ""
        productname = self._productname
        testname = self._testname
        casename = self._casename
        if (self._exact == False):
            extension = "~"
        if (not productname):
            productname = "*"
        if (not testname):
            testname = "*"
        if (not casename):
            casename = "*"
        return productname + "." + testname + "." + casename + extension
    
    def __eq__(self, other):
        if (self._productname == other._productname):
            if (self._testname == other._testname):
                if (self._casename == other._casename):
                    if (self._exact == other._exact):
                        return True;
        return False;

    def Clone(self):
        '''
        Returns a clone of the object.
        
        Return:
            Returns a newly created instance of SigQCTestCaseID that matches this
            test case identifier.
        '''
        return SigQCTestCaseID(self._productname, self._testname, self._casename, self._exact)
    
    def GetCaseName(self):
        '''
        Return the string representing the targeted test case name.
        '''
        return self._casename
    
    def GetTestName(self):
        '''
        Return the string representing the name of the acceptance test that contains
        the targeted test case.
        '''
        return self._testname
      
    def GetProductName(self):
        '''
        Return the string representing the name of the product that contains
        the targeted test case.
        '''
        return self._productname
    
    def IsEmpty(self):
        '''
        Determine whether or not the test case identifier does not contain either an acceptance
        test or test case name.
        
        Return:
            If True, then the neither the product, test, or case name have been specified.  If False,
            at least one of them have been specified.
        '''
        if (self._productname or self._testname or self._casename):
            return False
        return True
    
    def IsExact(self):
        '''
        Determine if this represents an exact test case identification or not.  Inexact
        identifiers are often used to target multiple test cases that contain a partial
        common name.  For example "[GO] RL Start Click" and "[GC] RR Start Click" both
        contain the text "Start Click".  Thus, an inexact test case identifier could be
        constructed with a test case name of "Start Click" only and assigning the exactness
        as False.  This functionality is most commonly used when working with test case
        groups.
        
        Return:
            If True, then the product, acceptance test, and test case names are defined
            exactly as they appear in the SigQC product database tree.  If False, then the
            identifier is targeting test cases for at least partial names.
            
        Note:
            If either the product, test, or case name is empty, then by definition the
            test case identifier is inexact.
        '''
        if (self._productname and self._testname and self._casename):
            return self._exact
        return False;
    
    def IsMatch(self, i_identifier):
        '''
        Determine whether or not the given test case identifier matches this
        test case identifier.  If both are defined as exact identifiers, all
        fields are compared.  If only one of the test case identifiers is exact,
        then the two are considered a match if the exact identifier "contains"
        the inexact identifier.  If both are inexact, comparison is performed
        on the lesser string of each the product names, test names, and case
        names.
        
        Example:
            x = SigQCTestCaseID("X15", "PHASE 1", "[P1] RL Start Click", True)
            y = SigQCTestCaseID("X15", "PHASE 1", "Start Click", False)
            state = y.IsMatch(x)
            print( x.__str__() + "\n" + y.__str__() + "\nMatch: ", state )

            y.SetExact(True)
            state = y.IsMatch(x)
            print( "\n" + x.__str__() + "\n" + y.__str__() + "\nMatch: ", state )

            <<<<<<<<<<<<<<<<<< Output >>>>>>>>>>>>>>>>>>>>>>>>>>>>
            X15.PHASE 1.[P1] RL Start Click
            X15.PHASE 1.Start Click~
            Match:  True

            X15.PHASE 1.[P1] RL Start Click
            X15.PHASE 1.Start Click
            Match:  False
        '''
        state = True
        # Compare exact test and case names from given identifier to this identifier...
        if ( (self.IsExact() == True) and (i_identifier.IsExact() == True)):
            state = (self == i_identifier)
        
        # Compare containment of test and case names from given identifier to this identifier...
        elif ( (self.IsExact() == True) and (i_identifier.IsExact() == False)):
            if (i_identifier._productname):
                state &= (i_identifier._productname in self._productname)
            if (i_identifier._testname):
                state &= (i_identifier._testname in self._testname)
            if ( i_identifier._casename):
                state &= (i_identifier._casename in self._casename)
                
        # Compare containment of test and case names from this identifier to the given identifier...
        elif ( (self.IsExact() == False) and (i_identifier.IsExact() == True)):
            if (self._productname):
                state &= (self._productname in i_identifier._productname)
            if (self._testname):
                state &= (self._testname in i_identifier._testname)
            if ( self._casename):
                state &= (self._casename in i_identifier._casename)
                
        # Compare containment of the shorter of test and case names since both are inexact...
        else:
            if (len(self._productname) > len(i_identifier._productname)):
                state &= (i_identifier._productname in self._productname)
            else:
                state &= (self._productname in i_identifier._productname)
            if (len(self._testname) > len(i_identifier._testname)):
                state &= (i_identifier._testname in self._testname)
            else:
                state &= (self._testname in i_identifier._testname)
            if (len(self._casename) > len(i_identifier._casename)):
                state &= (i_identifier._casename in self._casename)
            else:
                state &= (self._casename in i_identifier._casename)
        return state
    
    def Parse(self, i_string):
        '''
        Parse the product, acceptance test and test case names from a period (".") delimited
        string.
        
        Input:
            i_string - Specify a string in the form of "product.test.case".
            
        Note:
            If the last character of the case name contains the '~' character it is stripped
            from the final case name and the test case identifier is marked as inexact.
            
            If any of the product, test, or case names are the asterisk character ("*"), the
            name is assumed to be empty.
            
        Example:
            x = SigQCTestCaseID()
            x.Parse("X15.*.[P1] RL Start Click")
            print(x)
            x.Parse("X15.PHASE 1.Start Click~")
            print(x)
            x.SetExact(True)
            print(x)
            
            <<<<<<<<<<<<<<<<<< Output >>>>>>>>>>>>>>>>>>>>>>>>>>>>
            X15.*.[P1] RL Start Click
            X15.PHASE 1.Start Click~
            X15.PHASE 1.Start Click
        '''
        if (isinstance(i_string,str) == True):
            text  = i_string.split(".")
            count = len(text)
            if (count >= 3):
                self._exact = True;
                self._productname = text[0]
                self._testname = text[1]
                self._casename = text[2]
                if (self._casename.endswith("~") == True):
                    self._casename = self._casename[:-1]
                    self._exact = False;
                if ( self._productname == "*"):
                    self._productname = ""
                if ( self._testname == "*"):
                    self._testname = ""
                if ( self._casename == "*"):
                    self._casename = ""
            
    def Set(self, i_productname, i_testname, i_casename, i_exact=True):
        '''
        Specify the acceptance test and test case names that uniquely
        identify a test case within a given product.
        
        Input:
            i_productname - Specify a string that represents the name of the product
                            that contains the targeted test case.
                            
            i_testname    - A string representing the acceptance test name
                            that contains the targeted test case.
                         
            i_casename    - A string containing the targeted test case name.
            
            i_exact       - True indicates that you are defining the product, test, and test case
                            names exactly as they appear in the SigQC product database tree.  If
                            False, then the identifier is targeting test cases based on partial names.
        '''
        self._productname = i_productname
        self._testname = i_testname
        self._casename = i_casename
        self._exact = i_exact
        
    def Set(self,i_identifier):
        '''
        Assign this test case identifier from the given test case
        identifier.
        
        Input:
            i_identifier - Instance of the SigQCTestCaseID class from which
                           the acceptance test and test case names will be
                           copied.
        '''
        if (isinstance(self, SigQCTestCaseID) == True):
            self._productname = i_identifier._productname
            self._testname = i_identifier._testname
            self._casename = i_identifier._casename
            self._exact = i_identifier._exact
            
    
    def SetExact(self, i_exact):
        '''
        Specify whether or not this represents an exact test case identification.  Inexact
        identifiers are often used to target multiple test cases that contain a partial
        common name.  For example "[GO] RL Start Click" and "[GC] RR Start Click" both
        contain the text "Start Click".  Thus, an inexact test case identifier can be
        used to target multiple test cases.
        
        Input:
            i_exact - True indicates that you are defining the acceptance test and test case
                      names exactly as they appear in the SigQC product database tree.  If
                      False, then the identifier is targeting test cases for partial names.
                      
        Note:
            When a test case identifier is not exact, a "~" is appended to the printed format
            of the identifier.  The printed form is "product.test.case~".
        '''
        self._exact = i_exact

    def SetTestName(self, i_testname):
        '''
        Assign the acceptance test name.
        
        Input:
            i_testname - Specify a string that represents the name of the acceptance
                         test that contains the targeted test case.
        '''
        self._testname = i_testname
        
    def SetCaseName(self, i_casename):
        '''
        Assign the test case name.
        
        Input:
            i_casename - Specify a string that represents the name of the targeted
                         test case.
        '''
        self._casename = i_casename;
            
    def SetProductName(self, i_productname):
        '''
        Assign the product name.
        
        Input:
            i_productname - Specify a string that represents the name of the product
                            that contains the targeted test case.
        '''
        self._productname = i_productname

class SigQCTestCaseGroup(object):
    '''
    The SigQCTestCaseGroup class is designed to represent a list of test case identifiers that
    should be grouped together for the purpose of data display, review and analysis.  The group
    is based on instances of the SigQCTestCaseID class.
    '''
    def __init__(self):
        self._identifiers = []
        
    def __str__(self):
        text  = ""
        count = len(self._identifiers)
        for i in range(0,count):
            text += self._identifiers[i].__str__()
            if (i < count-1):
                text += "\n"
        return text
    
    def __getitem__(self, i_index):
        return self._identifiers[i_index]
    
    def __setitem__(self, i_index, i_value):
        if (i_index < self.Count()):
            self._identifiers[i_index] = i_value.Clone()
        elif (i_index == self.Count()):
            self.Append(i_value)
        else:
            self._identifiers[i_index]= i_value;

    def Append(self, i_object):
        '''
        Append a copy of one or multiple test case identifiers to the group.
        
        Input:
            i_object - Specify an instance of the SigQCTestCaseID, a list of identifier objects,
                       a test case group, or a period (".") delimited string of the form
                       "product.test.case".
                       
        Example:
            x = SigQCTestCaseGroup()
            a = SigQCTestCaseID("X15", "PHASE 1", "[P1] RL Start Click")
            x.Append(a)
            a.SetCaseName("[P1] RR Start Click")
            x.Append(a)
            a.SetCaseName("[P1] RL End Click")
            x.Append(a)
            a.SetCaseName("[P1] RR End Click")
            x.Append(a)
            print(x)        

            <<<<<<<<<<<<<<<<<< Output >>>>>>>>>>>>>>>>>>>>>>>>>>>>
            X15.PHASE 1.[P1] RL Start Click
            X15.PHASE 1.[P1] RR Start Click
            X15.PHASE 1.[P1] RL End Click
            X15.PHASE 1.[P1] RR End Click
        '''
        # If the given object is a SigQCTestCaseID, add a clone of the given test case identifier...
        if (isinstance(i_object,SigQCTestCaseID) == True):
            self._identifiers.append(i_object.Clone())
            
        # If the given object is another test case group, append the contents of the given group...
        elif (isinstance(i_object,SigQCTestCaseGroup) == True):
            self.Append(i_object._identifiers)
                
        # Parse the string according to the print format...
        elif (isinstance(i_object,str) == True):
            identifier = SigQCTestCaseID()
            identifier.Parse(i_object)
            if (identifier.IsEmpty() == False):
                self._identifiers.append(identifier)    
        
        # If the given object is a list, attempt to append all items in the list...
        elif (isinstance(i_object,list) == True):
            for i in range(0,len(i_object)):
                self.Append(i_object[i])

    def AppendByNames(self,i_productname,i_testname,i_casename,i_exact=True):
        '''
        Append a new test case identifier based on its product, test, and test
        case name.
        
        Input:
            i_productname - Specify the name of the product within which the test
                            case resides.
                            
            i_testname    - Specify the name of the acceptance test within which
                            the test case resides.
                            
            i_casename    - Specify the name of the test case.
            
            i_exact       - If True, the product, test, and case name appear exactly
                            as it is in the SigQC product database tree,  If False,
                            the given names are partial names.
        '''
        self.Append( SigQCTestCaseID(i_productname, i_testname, i_casename, i_exact) )
        
    def Clear(self):
        '''
        Clear the list of test case identifiers of the group.
        '''
        self._identifiers.clear()

    def Clone(self):
        '''
        Clone the test group and its content.
        
        Return:
            An newly created instance of the SigQCTestCaseGroup class that represents
            a duplicate of all test case identifiers defined in this group.
            
        Example:
            x = SigQCTestCaseGroup()
            a = SigQCTestCaseID("X15", "PHASE 1", "[P1] RL Start Click")
            x.Append(a)
            a.SetCaseName("[P1] RR Start Click")
            x.Append(a)
            a.SetCaseName("[P1] RL End Click")
            x.Append(a)
            a.SetCaseName("[P1] RR End Click")
            x.Append(a)

            y = x.Clone()
            print("X")
            print(x)        
            print("\nY")
            print(y)        

            <<<<<<<<<<<<<<<<<< Output >>>>>>>>>>>>>>>>>>>>>>>>>>>>
            X
            X15.PHASE 1.[P1] RL Start Click
            X15.PHASE 1.[P1] RR Start Click
            X15.PHASE 1.[P1] RL End Click
            X15.PHASE 1.[P1] RR End Click

            Y
            X15.PHASE 1.[P1] RL Start Click
            X15.PHASE 1.[P1] RR Start Click
            X15.PHASE 1.[P1] RL End Click
            X15.PHASE 1.[P1] RR End Click        '''
        group = SigQCTestCaseGroup()
        count = self.Count()
        for i in range(0,count):
            group.Append(self[i])
        return group
        
    def Count(self):
        '''
        Determine the number of test case identifiers managed by the group.
        '''
        return len(self._identifiers)
        
    def CountUniqueCaseNames(self):
        '''
        Determine the number of unique test case names managed by the group.
        
        Return:
            int - Represents the number of unique test case names managed within the
                  group.  Empty test case names are not counted.
                  
        Note:
            This method only compares the test case names for uniqueness.  Test case
            identifiers that have the same test case name, but differ by product or
            test are not considered unique.
        '''
        return len(self.GetUniqueCaseNames())
        
    def CountUniqueProductNames(self):
        '''
        Determine the number of unique product names managed by the group.
        
        Return:
            int - Represents the number of unique product names managed within the
                  group.  Empty product names are not counted.
        '''
        return len(self.GetUniqueProductNames())
        
    def CountUniqueTestNames(self):
        '''
        Determine the number of unique acceptance test names managed by the group.
        
        Return:
            int - Represents the number of unique acceptance test names managed within
                  the group.  Empty acceptance test names are not counted.
                  
        Note:
            This method only compares the acceptance test names for uniqueness.  Test
            case identifiers that have the same acceptance test name, but differ by
            product are not considered unique.
        '''
        return len(self.GetUniqueTestNames())
        
    def CountUniqueProducts(self):
        '''
        Determine the number of unique products managed by the group.
        
        Return:
            int - Represents the number of unique products managed within the
                  group.  Empty product identifiers are not counted.
        '''
        return len(self.GetUniqueProductNames())
    
    def Contains(self, i_identifier):
        '''
        Determine whether or not test case group contains a specific test case identifier.
        Comparison is made by direct comparison of all fields using the equivalence
        operator.
        
        Input:
            i_identifier - Instance of the SigQCTestCaseID class to be located.
            
        Return:
            An int value that represents the index of the test case identifier
            within the group.  Return a value of -1 if the targeted test case
            identifier does not exist within the test case group.
        '''
        index = -1
        count = self.Count()
        for i in range(0,count):
            if (self._identifiers[i] == i_identifier):
                index = i;
                break;
        return index;          
    
    def FindMatchingIDsOf(self, i_object):
        '''
        Create a test case group that contains all of the matching test case identifiers
        within this test case group.  The purpose is to locate test case identifiers within
        the group that either "fully" or "partially" match the given object.  Internally,
        partial matching is accomplished using the SigQCTestCaseID.IsMatch() method, so
        reference that method for details.
        
        Input:
            i_object - Specify an instance of the SigQCTestCaseGroup, SigQCTestCaseID, or
                       a string of the form "product.test.case" whose matching test case
                       group will be constructed.
        
        Example:
            group1 = SigQCTestCaseGroup()
            group1.AppendByNames("X15", "PHASE 1", "[P1] RL Start Click")
            group1.AppendByNames("X15", "PHASE 1", "[P1] RR Start Click")
            group1.AppendByNames("X15", "PHASE 1", "[P1] RL End Click")
            group1.AppendByNames("X15", "PHASE 1", "[P1] RR End Click")
            group1.AppendByNames("X15", "PHASE 2", "[P2] RL Start Click")
            group1.AppendByNames("X15", "PHASE 2", "[P2] RR Start Click")
            group1.AppendByNames("X15", "PHASE 2", "[P2] RL End Click")
            group1.AppendByNames("X15", "PHASE 2", "[P2] RR End Click")
            print("GROUP1\n" + group1.__str__())

            group2 = SigQCTestCaseGroup()
            group2.AppendByNames("", "", "Start Click", False)
            print("\nGROUP2\n" + group2.__str__())

            group3 = group1.FindMatchingIDsOf(group2)
            print("\nGROUP3\n" + group3.__str__())

            <<<<<<<<<<<<<<<<<< Output >>>>>>>>>>>>>>>>>>>>>>>>>>>>
            GROUP1
            X15.PHASE 1.[P1] RL Start Click~
            X15.PHASE 1.[P1] RR Start Click~
            X15.PHASE 1.[P1] RL End Click~
            X15.PHASE 1.[P1] RR End Click~
            X15.PHASE 2.[P2] RL Start Click~
            X15.PHASE 2.[P2] RR Start Click~
            X15.PHASE 2.[P2] RL End Click~
            X15.PHASE 2.[P2] RR End Click~

            GROUP2
            *.*.Start Click

            GROUP3
            X15.PHASE 1.[P1] RL Start Click~
            X15.PHASE 1.[P1] RR Start Click~
            X15.PHASE 2.[P2] RL Start Click~
            X15.PHASE 2.[P2] RR Start Click~

        '''
        group = None
        if ( isinstance(i_object, SigQCTestCaseGroup) == True):
            group = SigQCTestCaseGroup()
            count = i_object.Count()
            for i in range(0,count):
                group.Append(self.FindMatchingIDsOf(i_object[i]))
        elif (isinstance(i_object,SigQCTestCaseID) == True):
            group = SigQCTestCaseGroup()
            count = self.Count()
            for i in range(0, count):
                if ( self[i].IsMatch(i_object) == True ):
                    group.Append(self[i])
        elif (isinstance(i_object,str) == True):
            group = SigQCTestCaseGroup()
            count = self.Count()
            for i in range(0, count):
                identifier = SigQCTestCaseID()
                identifier.Parse(i_object)
                if ( self[i].IsMatch(identifier) == True ):
                    group.Append(self[i])
        return group;
    
    def GetUniqueProductNames(self):
        '''
        Get a list of all unique product names within the test case group.
        
        Return:
            A list of strings that represent the unique product names within the
            test case group.  Empty product names are not returned in the list.
        '''
        productnames = []
        for i in range(0,self.Count()):
            productname = self._identifiers[i]._productname
            if (productname not in productnames):
                productnames.append(productname)
        return productnames
    
    def GetUniqueTestNames(self):
        '''
        Get a list of all unique product names within the test case group.
        
        Return:
            A list of strings that represent the unique acceptance test names within
            the test case group.  Empty acceptance test names are not returned in
            the list.
        '''
        testnames = []
        for i in range(0,self.Count()):
            testname = self._identifiers[i]._testname
            if (testname not in testnames):
                testnames.append(testname)
        return testnames
    
    def GetUniqueCaseNames(self):
        '''
        Get a list of all unique test case names within the test case group.
        
        Return:
            A list of strings that represent the unique test case names within the
            test case group.  Empty test case names are not returned in the list.
        '''
        casenames = []
        for i in range(0,self.Count()):
            casename = self._identifiers[i]._casename
            if (casename not in casenames):
                casenames.append(casename)
        return casenames

    def IsEmpty(self):
        '''
        Determine if this test case group is empty or not.
        
        Return:
            If True, the test case group is empty.  If False, at least one
            test case identifier exists.
        '''
        return (self.Count() == 0)

    def MakeUniqueGroup(self):
        '''
        Create a copy of this test case group that excludes duplicate test case identifiers.
        
        Return:
            A newly created SigQCTestCaseGroup class that contains a copy of the unique
            test case identifiers from this test case group.
            
        Example:
            x = SigQCTestCaseGroup()
            a = SigQCTestCaseID("X15", "PHASE 1", "[P1] RL Start Click")
            x.Append(a)
            x.Append(a)
            a.SetCaseName("[P1] RR Start Click")
            x.Append(a)
            x.Append(a)
            print("X\n" + x.__str__())

            y = x.MakeUniqueGroup()
            print("\nY\n" + y.__str__())

            <<<<<<<<<<<<<<<<<< Output >>>>>>>>>>>>>>>>>>>>>>>>>>>>
            X
            X15.PHASE 1.[P1] RL Start Click
            X15.PHASE 1.[P1] RL Start Click
            X15.PHASE 1.[P1] RR Start Click
            X15.PHASE 1.[P1] RR Start Click

            Y
            X15.PHASE 1.[P1] RL Start Click
            X15.PHASE 1.[P1] RR Start Click
        '''
        group = SigQCTestCaseGroup()
        count = self.Count()
        for i in range(0,count):
            if (group.Contains(self[i]) == -1):
                group.Append(self[i].Clone())
        return group

    def ListGroupsByCase(self):
        '''
        Create a list of test case groups that are based on a common product name.
        
        Return:
            A list of SigQCTestCaseGroup objects that represent separate groups of test
            test case identifiers that share a common product name.
            
        Example:
            x = SigQCTestCaseGroup()
            x.Append("X15.PHASE1.RL Start Click")
            x.Append("X15.PHASE1.RR Start Click")
            x.Append("X16.PHASE1.RL Start Click")
            x.Append("X16.PHASE1.RR Start Click")
            x.Append("X17.PHASE1.RL Start Click")
            x.Append("X17.PHASE1.RR Start Click")
            x.Append("X18.PHASE1.RL Start Click")
            x.Append("X18.PHASE1.RR Start Click")

            casegroups = x.ListGroupsByCase()
            if (casegroups is not None):
                for i in range(0,len(casegroups)):
                    print(casegroups[i])
                    print("\n")

            <<<<<<<<<<<<<<<<<< Output >>>>>>>>>>>>>>>>>>>>>>>>>>>>
        
            X15.PHASE1.RL Start Click
            X16.PHASE1.RL Start Click
            X17.PHASE1.RL Start Click
            X18.PHASE1.RL Start Click


            X15.PHASE1.RR Start Click
            X16.PHASE1.RR Start Click
            X17.PHASE1.RR Start Click
            X18.PHASE1.RR Start Click
        '''
        groups = []
        casenames = self.GetUniqueCaseNames()
        for i in range(0,len(casenames)):
            group = self.FindMatchingIDsOf(".."+casenames[i])
            if (group is not None):
                groups.append(group)
        return groups

    def ListGroupsByProduct(self):
        '''
        Create a list of test case groups that are based on a common product name.
        
        Return:
            A list of SigQCTestCaseGroup objects that represent separate groups of test
            test case identifiers that share a common product name.
            
        Example:
            x = SigQCTestCaseGroup()
            x.Append("X15.PHASE1.RL Start Click")
            x.Append("X15.PHASE1.RR Start Click")
            x.Append("X16.PHASE1.RL Start Click")
            x.Append("X16.PHASE1.RR Start Click")
            x.Append("X17.PHASE1.RL Start Click")
            x.Append("X17.PHASE1.RR Start Click")
            x.Append("X18.PHASE1.RL Start Click")
            x.Append("X18.PHASE1.RR Start Click")

            productgroups = x.ListGroupsByProduct()
            if (productgroups is not None):
                for i in range(0,len(productgroups)):
                    print(productgroups[i])
                    print("\n")

            <<<<<<<<<<<<<<<<<< Output >>>>>>>>>>>>>>>>>>>>>>>>>>>>
        
            X15.PHASE1.RL Start Click
            X15.PHASE1.RR Start Click


            X16.PHASE1.RL Start Click
            X16.PHASE1.RR Start Click


            X17.PHASE1.RL Start Click
            X17.PHASE1.RR Start Click


            X18.PHASE1.RL Start Click
            X18.PHASE1.RR Start Click
        '''
        groups = []
        productnames = self.GetUniqueProductNames()
        for i in range(0,len(productnames)):
            group = self.FindMatchingIDsOf(productnames[i]+"..")
            if (group is not None):
                groups.append(group)
        return groups

    
    def ListGroupsByTest(self):
        '''
        Create a list of test case groups that are based on a common acceptance test name.
        
        Return:
            A list of SigQCTestCaseGroup objects that represent separate groups of test
            test case identifiers that share a common acceptance test name.
            
        Example:
            x = SigQCTestCaseGroup()
            x.Append("X15.PHASE1.RL Start Click")
            x.Append("X15.PHASE1.RR Start Click")
            x.Append("X15.PHASE2.RL Start Click")
            x.Append("X15.PHASE2.RR Start Click")
            x.Append("X15.PHASE3.RL Start Click")
            x.Append("X15.PHASE3.RR Start Click")
            x.Append("X15.PHASE4.RL Start Click")
            x.Append("X15.PHASE4.RR Start Click")

            testgroups = x.ListGroupsByTest()
            if (testgroups is not None):
                for i in range(0,len(testgroups)):
                    print("\n")
                    print(testgroups[i])

            <<<<<<<<<<<<<<<<<< Output >>>>>>>>>>>>>>>>>>>>>>>>>>>>
        
            X15.PHASE1.RL Start Click
            X15.PHASE1.RR Start Click

            X15.PHASE2.RL Start Click
            X15.PHASE2.RR Start Click

            X15.PHASE3.RL Start Click
            X15.PHASE3.RR Start Click

            X15.PHASE4.RL Start Click
            X15.PHASE4.RR Start Click
        '''
        groups = []
        testnames = self.GetUniqueTestNames()
        for i in range(0,len(testnames)):
            group = self.FindMatchingIDsOf("."+testnames[i]+".")
            if (group is not None):
                groups.append(group)
        return groups

class SigQCTestCaseGroupMatrix(object):
    '''
    The SigQCTestCaseGroupMatrix class is designed to represent a matrix of test case groups
    that define the location of test cases when displayed in a panel type display.
    '''
    def __init__(self,i_rows=2,i_columns=2):
        '''
        Initialize the test case group matrix for a specific number of rows and columns.
        
        Example:
            x = SigQCTestCaseGroupMatrix()
        '''
        self._groups = np.empty((i_rows,i_columns),dtype=object)
        for i in range(0,i_rows):
            for j in range(0,i_columns):
                self._groups[i,j] = SigQCTestCaseGroup()            
    
    def __getitem__(self, i_cell):
        '''
        Overrides the index operator to allow accessing the test case group content
        by tuple index.  Return None if the specified index is out of range.
        
        Example:
            x = SigQCTestCaseGroupMatrix( 4, 2 )
            x[0,0].Append("X15.PHASE1.RL Start Click")
            x[0,1].Append("X15.PHASE1.RR Start Click")
            print(x[0,1])

            <<<<<<<<<<<<<<<<<< Output >>>>>>>>>>>>>>>>>>>>>>>>>>>>
            X15.PHASE1.RR Start Click
        '''
        row, col = i_cell
        rows, cols = self._groups.shape
        if ((row < rows) and (col < cols)):
            return self._groups[row,col]
        return None
    
    def __setitem__(self, i_cell, i_testcasegroup):
        '''
        Overrides the index assignment operator to allow assigning a test case group to
        a specific cell of the matrix.
        
        Input:
            i_cell          - Tuple in the form of (row,col) that identifies the cell to be
                              assigned.
                     
            i_testcasegroup - Instance of the SigQCTestCaseGroup class that defines the test
                              case identifiers associated with the targeted cell.  A copy of
                              the given test case group is made.
        
        Example:
            x = SigQCTestCaseGroupMatrix( 4, 2 )
            x[0,0].Append("X15.PHASE1.RL Start Click")
            x[0,1].Append("X15.PHASE1.RR Start Click")
            x[1,0].Append("X15.PHASE2.RL Start Click")
            x[1,1].Append("X15.PHASE2.RR Start Click")
            x[2,0].Append("X15.PHASE3.RL Start Click")
            x[2,1].Append("X15.PHASE3.RR Start Click")
            x[3,0].Append("X15.PHASE4.RL Start Click")
            x[3,1].Append("X15.PHASE4.RR Start Click")
            x[3,1].Append("X15.PHASE4.RL End Click")
            x[3,1].Append("X15.PHASE4.RR End Click")
            print(x)

            <<<<<<<<<<<<<<<<<< Output >>>>>>>>>>>>>>>>>>>>>>>>>>>>
            X15.PHASE1.RL Start Click	X15.PHASE1.RR Start Click	

            X15.PHASE2.RL Start Click	X15.PHASE2.RR Start Click	

            X15.PHASE3.RL Start Click	X15.PHASE3.RR Start Click	

            X15.PHASE4.RL Start Click	X15.PHASE4.RR Start Click	
                                        X15.PHASE4.RL End Click 	
                                        X15.PHASE4.RR End Click 	
        '''
        if (isinstance(i_testcasegroup, SigQCTestCaseGroup) == True):
            row, col = i_cell
            rows, cols = self._groups.shape
            if ((row < rows) and (col < cols)):
                self._groups[row,col] = i_testcasegroup.Clone()
        return
    
    def __str__(self):
        text = ""
        item = ""
        line = ""
        rows = self.CountRows();
        cols = self.CountColumns();
        text = "(" + self.CountRows().__str__() + " x " + self.CountColumns().__str__() + ")\n"
        # Find the maximum number of characters in any column...
        maxchar = 0
        for i in range(0,rows):
            for j in range(0,cols):
                if (self[i,j] is not None):
                    for k in range(0,self[i,j].Count()):
                        if (len(self[i,j][k].__str__()) > maxchar):
                            maxchar = len(self[i,j][k].__str__());
        
        for i in range(0,rows):            
            # First, count the maximum number of test case identifiers among all test case groups
            # within the current row...
            maxitems = 0
            for j in range(0,cols):
                if (self[i,j] is not None):
                    if (self[i,j].Count() > maxitems):
                        maxitems = self[i,j].Count()
                        
            # Next, loop through each column of the current row to form the text line
            # for this row....           
            if ( maxitems == 0):
                maxitems = 1
            for k in range(0,maxitems):
                for j in range(0,cols):
                    if (self[i,j] is not None):
                        if (k < self[i,j].Count()):
                            item = (self[i,j])[k].__str__();
                        else:
                            item = ""
                    else:
                        item = ""
                        
                    while (len(item) < maxchar-1):
                        item += " "
                    line += item
                    line += "\t"
                        
                # We have formed one line of the output so add a newline character and continue...
                text += line;
                text += "\n"
                line = ""
                
            # Finished with row, so add an extra newline for spacing...
            text += "\n"
        return text
    
    def Shape(self):
        return (self._groups.shape)
    
    def CountColumns(self):
        '''
        Determine the number of columns allocated for the test case group matrix.
        '''
        rows, cols = self._groups.shape
        return cols
    
    def CountRows(self):
        '''
        Determine the number of rows allocated for the test case group matrix.
        '''
        rows, cols = self._groups.shape
        return rows

    def ConfigureByTest(self,i_group,i_product,i_casename):
        '''
        Given a single SigQCTestCaseGroup, configure a matrix that represents a subset of
        the group organized by tests on the rows and common test case names as columns.
        
        Example:
            i_group = SigQCTestCaseGroup()
            i_group.Append("X15.PHASE1.RL Start Click")
            i_group.Append("X15.PHASE1.RR Start Click")
            i_group.Append("X15.PHASE1.RL Cutout Engage")
            i_group.Append("X15.PHASE1.RR Cutout Engage")
            i_group.Append("X15.PHASE1.RL End Click")
            i_group.Append("X15.PHASE1.RR End Click")
            i_group.Append("X15.PHASE2.RL Start Click")
            i_group.Append("X15.PHASE2.RR Start Click")
            i_group.Append("X15.PHASE2.RL Cutout Disengage")
            i_group.Append("X15.PHASE2.RR Cutout Disengage")
            i_group.Append("X15.PHASE2.RR Deflector Engage")
            i_group.Append("X15.PHASE2.RL Deflector Engage")
            i_group.Append("X15.PHASE2.RL End Click")
            i_group.Append("X15.PHASE2.RR End Click")
            i_group.Append("X15.PHASE3.RL Start Click")
            i_group.Append("X15.PHASE3.RR Start Click")
            i_group.Append("X15.PHASE3.RL End Click")
            i_group.Append("X15.PHASE3.RR End Click")
            i_group.Append("X15.PHASE4.RL Start Click")
            i_group.Append("X15.PHASE4.RR Start Click")
            i_group.Append("X15.PHASE4.RL End Click")
            i_group.Append("X15.PHASE4.RR End Click")

            # Create a test case matrix and fill it using partialall of the test case identifiers that
            # contain the label "RL Cutout"...
            y = SigQCTestCaseGroupMatrix()
            y.ConfigureByTest(i_group,"","RL Cutout")
            print("\n")
            print(y)
            
            <<<<<<<<<<<<<<<<<< Output >>>>>>>>>>>>>>>>>>>>>>>>>>>>
            (2 x 2)
            *.PHASE1.RL Cutout Engage  	*.PHASE1.RL Cutout Disengage	

            *.PHASE2.RL Cutout Engage  	*.PHASE2.RL Cutout Disengage	
        '''
        # First, extract the product group if specified...
        productgroup = i_group.FindMatchingIDsOf(i_product+".*."+i_casename)
        testnames = productgroup.GetUniqueTestNames()
        casenames = productgroup.GetUniqueCaseNames()
        rows = len(testnames)
        columns = len(casenames)

        # Reconfigure the member _groups variable according to the determined rows and columns
        self._groups = np.empty((rows,columns),dtype=object)
        for i in range(0,rows):
            for j in range(0,columns):
                self._groups[i,j] = SigQCTestCaseGroup()
                if ( productgroup.Contains(SigQCTestCaseID(i_product,testnames[i],casenames[j]))):
                    self._groups[i,j].AppendByNames(i_product,testnames[i],casenames[j])

