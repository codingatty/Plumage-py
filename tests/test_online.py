#! python2
import unittest
from Plumage import plumage

class TestUM(unittest.TestCase):
 
    def setUp(self):
        pass

    def _validate_sample(self, t):
        '''
        Test to confirm content for Python trademark; whether as
        app no. 76/044,902 or ser. no.  2824281
        '''
        self.assertTrue(t.XMLDataIsValid)
        self.assertEqual(t.XMLData[0:55], r'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
        self.assertTrue(t.CSVDataIsValid)
        tsdrdata=t.TSDRData
        self.assertTrue(tsdrdata.TSDRMapIsValid)
        self.assertEqual(tsdrdata.TSDRSingle["ApplicationNumber"], "76044902")
        self.assertEqual(tsdrdata.TSDRSingle["ApplicationDate"], "2000-05-09-04:00")
        self.assertEqual(tsdrdata.TSDRSingle["ApplicationDate"][0:10],
                         tsdrdata.TSDRSingle["ApplicationDateTruncated"])
        self.assertEqual(tsdrdata.TSDRSingle["RegistrationNumber"], "2824281")
        if tsdrdata.TSDRSingle["DiagnosticInfoXSLTFormat"] == "ST.96":  #ST.96 does not include time portion in reg date
            self.assertEqual(tsdrdata.TSDRSingle["RegistrationDate"], "2004-03-23")
        else:
            self.assertEqual(tsdrdata.TSDRSingle["RegistrationDate"], "2004-03-23-05:00")

        self.assertEqual(tsdrdata.TSDRSingle["RegistrationDate"][0:10],
                         tsdrdata.TSDRSingle["RegistrationDateTruncated"])
        self.assertEqual(tsdrdata.TSDRSingle["MarkVerbalElementText"], "PYTHON")
        applicant_list = tsdrdata.TSDRMulti["ApplicantList"]
        applicant_info = applicant_list[0]    
        self.assertEqual(applicant_info["ApplicantName"], "PYTHON SOFTWARE FOUNDATION")
        if t.PTOFormat != "ST66":   # non-zipped ST.66 format does not include assignments
            assignment_list = tsdrdata.TSDRMulti["AssignmentList"]
            assignment_0 = assignment_list[0] # Zeroth (most recent) assignment
            self.assertEqual(assignment_0["AssignorEntityName"],
                     "CORPORATION FOR NATIONAL RESEARCH INITIATIVES, INC.")
            self.assertEqual(assignment_0["AssignmentDocumentURL"],
                     "http://assignments.uspto.gov/assignments/assignment-tm-2849-0875.pdf")
        ## Diagnostic info
        self.assertEqual(tsdrdata.TSDRSingle["DiagnosticInfoXSLTURL"],
                         "https://github.com/codingatty/Plumage")
        self.assertEqual(tsdrdata.TSDRSingle["DiagnosticInfoXSLTLicense"],
                         "Apache License, version 2.0 (January 2004)")
        self.assertEqual(tsdrdata.TSDRSingle["DiagnosticInfoXSLTSPDXLicenseIdentifier"],
                         "Apache-2.0")
        self.assertEqual(tsdrdata.TSDRSingle["DiagnosticInfoXSLTLicenseURL"],
                         "http://www.apache.org/licenses/LICENSE-2.0")
        self.assertEqual(tsdrdata.TSDRSingle["DiagnosticInfoImplementationURL"],
                         "https://github.com/codingatty/Plumage-py")
        self.assertRegexpMatches(tsdrdata.TSDRSingle["DiagnosticInfoImplementationVersion"],
                         r"^\d+\.\d+\.\d+(-(\w+))*$")
        self.assertEqual(tsdrdata.TSDRSingle["DiagnosticInfoImplementationLicenseURL"],
                         "http://www.apache.org/licenses/LICENSE-2.0")
        self.assertEqual(tsdrdata.TSDRSingle["DiagnosticInfoImplementationLicense"],
                         "Apache License, version 2.0 (January 2004)")
        self.assertEqual(tsdrdata.TSDRSingle["DiagnosticInfoImplementationName"],
                         "Plumage-py")
        self.assertEqual(tsdrdata.TSDRSingle["DiagnosticInfoImplementationSPDXLicenseIdentifier"],
                         "Apache-2.0")

    def test_O001_zipfile_by_serialno(self):
        t = plumage.TSDRReq()
        t.getTSDRInfo("76044902", "s")
        self._validate_sample(t)

    def test_O002_zipfile_by_regno(self):
        t = plumage.TSDRReq()
        t.getTSDRInfo("2824281", "r")
        self._validate_sample(t)

    def test_O003_ST66xmlfile_by_serialno(self):
        t = plumage.TSDRReq()
        t.setPTOFormat("ST66")
        t.getTSDRInfo("76044902", "s")
        self._validate_sample(t)

    def test_O004_ST96xmlfile_by_serialno(self):
        t = plumage.TSDRReq()
        t.setPTOFormat("ST96")
        t.getTSDRInfo("76044902", "s")
        self._validate_sample(t)

    def test_O005_step_by_step(self):
        t = plumage.TSDRReq()
        self.assertFalse(t.XMLDataIsValid)
        self.assertFalse(t.CSVDataIsValid)
        self.assertFalse(t.TSDRData.TSDRMapIsValid)
        t.getXMLData("76044902", "s")
        self.assertTrue(t.XMLDataIsValid)
        self.assertFalse(t.CSVDataIsValid)
        self.assertFalse(t.TSDRData.TSDRMapIsValid)
        t.getCSVData()
        self.assertTrue(t.XMLDataIsValid)
        self.assertTrue(t.CSVDataIsValid)
        self.assertFalse(t.TSDRData.TSDRMapIsValid)
        t.getTSDRData()
        self.assertTrue(t.XMLDataIsValid)
        self.assertTrue(t.CSVDataIsValid)
        self.assertTrue(t.TSDRData.TSDRMapIsValid)
        self._validate_sample(t)
        t.resetXMLData()
        self.assertFalse(t.XMLDataIsValid)
        self.assertFalse(t.CSVDataIsValid)
        self.assertFalse(t.TSDRData.TSDRMapIsValid)

    def test_O099_no_such_app(self):
        '''
        Test no-such-application returns no data, and a Fetch-404 error code
        '''
        t = plumage.TSDRReq()
        t.getTSDRInfo("99999999", "s")
        self.assertFalse(t.XMLDataIsValid)
        self.assertFalse(t.CSVDataIsValid)
        self.assertFalse(t.TSDRData.TSDRMapIsValid)
        self.assertEqual(t.ErrorCode, "Fetch-404") 

if __name__ == '__main__':
    unittest.main(verbosity=5)
