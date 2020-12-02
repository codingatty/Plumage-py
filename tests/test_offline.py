import os
import sys
#import datetime as base_dt
from datetime  import datetime
from datetime  import timedelta
import time
import unittest

PYTHON2 = sys.version_info.major == 2
PYTHON3 = sys.version_info.major == 3

from testing_context import plumage

class TestUM(unittest.TestCase):

    # Group A: Basic exercises
    # Group B: XML fetch only
    # Group C: CSV creation
    # Group D: All the way through TSDR map
    # Group E: Parameter validations
    # Group F: XML/XSL variations
    # Group G: CSV/XSL validations
    # Group H: test add'l fields as added
    # Group I: test timing
    #  
    # Group O (in test_online.py): Online tests that actually hit the PTO TSDR system

    TESTFILES_DIR = "testfiles"
    # Save initial timing info for reset later 
    INITIAL_PRIOR_TSDR_CALL_TIME  = plumage.TSDRReq._prior_TSDR_call_time 
 
    def shortDescription(self):
        # suppress unit test displaying docstrings
        return None

    def setUp(self):
        # start each test with fresh prior-call time; tests with multiple TSDRReqs will need to reset themselves to avoid delay
        plumage.TSDRReq._prior_TSDR_call_time =  TestUM.INITIAL_PRIOR_TSDR_CALL_TIME 
        plumage.ResetIntervalTime()
        pass

    # Group A
    # Basic exercises

    def test_A001_test_initialize(self):
        '''
        Simple test, just verify TSDRReq can be initialized correctly
        '''
        t = plumage.TSDRReq()
        self.assertFalse(t.XMLDataIsValid)
        self.assertFalse(t.CSVDataIsValid)
        self.assertFalse(t.TSDRData.TSDRMapIsValid)

    def test_A002_step_by_step_and_reset(self):
        t = plumage.TSDRReq()
        self.assertFalse(t.XMLDataIsValid)
        self.assertFalse(t.CSVDataIsValid)
        self.assertFalse(t.TSDRData.TSDRMapIsValid)
        testfile = os.path.join(self.TESTFILES_DIR, "sn76044902.zip")
        t.getXMLData(testfile)
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
        t.resetXMLData()
        self.assertFalse(t.XMLDataIsValid)
        self.assertFalse(t.CSVDataIsValid)
        self.assertFalse(t.TSDRData.TSDRMapIsValid)
        
    def test_A003_typical_use(self):
        t = plumage.TSDRReq()
        testfile = os.path.join(self.TESTFILES_DIR, "sn76044902.zip")
        t.getTSDRInfo(testfile)
        self.assertTrue(t.XMLDataIsValid)
        self.assertEqual(len(t.XMLData), 30354)
        self.assertEqual(t.XMLData[0:55], r'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
        if PYTHON2:
            self.assertEqual(t.ImageThumb[6:10], "JFIF")
            self.assertEqual(t.ImageFull[0:4], "\x89PNG")
        if PYTHON3:
            self.assertEqual(t.ImageThumb[6:10], b"JFIF")
            self.assertEqual(t.ImageFull[0:4], b"\x89PNG")
        self.assertTrue(t.CSVDataIsValid)
        tsdrdata=t.TSDRData
        self.assertTrue(tsdrdata.TSDRMapIsValid)
        self.assertEqual(tsdrdata.TSDRSingle["ApplicationNumber"], "76044902")
        self.assertEqual(tsdrdata.TSDRSingle["ApplicationDate"], "2000-05-09-04:00")
        self.assertEqual(tsdrdata.TSDRSingle["ApplicationDate"][0:10],
                         tsdrdata.TSDRSingle["ApplicationDateTruncated"])
        self.assertEqual(tsdrdata.TSDRSingle["RegistrationNumber"], "2824281")
        self.assertEqual(tsdrdata.TSDRSingle["RegistrationDate"], "2004-03-23-05:00")
        self.assertEqual(tsdrdata.TSDRSingle["RegistrationDate"][0:10],
                         tsdrdata.TSDRSingle["RegistrationDateTruncated"])
        self.assertEqual(tsdrdata.TSDRSingle["MarkVerbalElementText"], "PYTHON")
        self.assertEqual(tsdrdata.TSDRSingle["MarkCurrentStatusExternalDescriptionText"],
                         "A Sections 8 and 15 combined declaration has been accepted and acknowledged.")
        self.assertEqual(tsdrdata.TSDRSingle["MarkCurrentStatusDate"], "2010-09-08-04:00")
        self.assertEqual(tsdrdata.TSDRSingle["MarkCurrentStatusDate"][0:10],
                         tsdrdata.TSDRSingle["MarkCurrentStatusDateTruncated"])
        applicant_list = tsdrdata.TSDRMulti["ApplicantList"]
        applicant_info = applicant_list[0]    
        self.assertEqual(applicant_info["ApplicantName"], "PYTHON SOFTWARE FOUNDATION")
        assignment_list = tsdrdata.TSDRMulti["AssignmentList"]
        assignment_0 = assignment_list[0] # Zeroth (most recent) assignment
        self.assertEqual(assignment_0["AssignorEntityName"],
                         "CORPORATION FOR NATIONAL RESEARCH INITIATIVES, INC.")
        self.assertEqual(assignment_0["AssignmentDocumentURL"],
                         "http://assignments.uspto.gov/assignments/assignment-tm-2849-0875.pdf")
        ## Diagnostic info
        self.assertEqual(tsdrdata.TSDRSingle["MetaInfoXSLTName"], "Plumage")
        if PYTHON2: # method renamed from assertRegexpMatches to assertRegex between Py2 and Py3
            self.assertRegexpMatches(tsdrdata.TSDRSingle["MetaInfoXSLTVersion"],
                         r"^\d+\.\d+\.\d+(-(\w+))*$")
        if PYTHON3:
            self.assertRegex(tsdrdata.TSDRSingle["MetaInfoXSLTVersion"],
                         r"^\d+\.\d+\.\d+(-(\w+))*$")
        # r"^\d+\.\d+\.\d+(-(\w+))*$"  :
        #   matches release number in the form "1.2.3", with an optional dashed suffix like "-prelease"
        self.assertEqual(tsdrdata.TSDRSingle["MetaInfoExecXSLTFormat"], "ST.66")
        self.assertEqual(tsdrdata.TSDRSingle["MetaInfoXSLTURL"],
                         "https://github.com/codingatty/Plumage")
        self.assertEqual(tsdrdata.TSDRSingle["MetaInfoXSLTLicense"],
                         "Apache License, version 2.0 (January 2004)")
        self.assertEqual(tsdrdata.TSDRSingle["MetaInfoXSLTSPDXLicenseIdentifier"],
                         "Apache-2.0")
        self.assertEqual(tsdrdata.TSDRSingle["MetaInfoXSLTLicenseURL"],
                         "http://www.apache.org/licenses/LICENSE-2.0")

        self.assertEqual(tsdrdata.TSDRSingle["MetaInfoLibraryName"], "Plumage-py")
        if PYTHON2: # method renamed from assertRegexpMatches to assertRegex between Py2 and Py3
            self.assertRegexpMatches(tsdrdata.TSDRSingle["MetaInfoLibraryVersion"],
                         r"^\d+\.\d+\.\d+(-(\w+))*$")
        if PYTHON3:
            self.assertRegex(tsdrdata.TSDRSingle["MetaInfoLibraryVersion"],
                         r"^\d+\.\d+\.\d+(-(\w+))*$")
        # r"^\d+\.\d+\.\d+(-(\w+))*$"  :
        #   matches release number in the form "1.2.3", with an optional dashed suffix like "-prelease"
        self.assertEqual(tsdrdata.TSDRSingle["MetaInfoLibraryURL"],
                         "https://github.com/codingatty/Plumage-py")
        self.assertEqual(tsdrdata.TSDRSingle["MetaInfoLibraryLicense"],
                         "Apache License, version 2.0 (January 2004)")
        self.assertEqual(tsdrdata.TSDRSingle["MetaInfoLibrarySPDXLicenseIdentifier"],
                         "Apache-2.0")
        self.assertEqual(tsdrdata.TSDRSingle["MetaInfoLibraryLicenseURL"],
                         "http://www.apache.org/licenses/LICENSE-2.0")

        # Execution-time fields

        simple_timestamp = tsdrdata.TSDRSingle["MetaInfoExecExecutionDateTime"]
        ts_as_datetime = datetime.strptime(simple_timestamp, "%Y-%m-%d %H:%M:%S") # we convert time w/o (no ValuError)
        ts_as_text = datetime.strftime(ts_as_datetime, "%Y-%m-%d %H:%M:%S")  # confirm round-trip conversion okay
        self.assertEqual(simple_timestamp, ts_as_text)

        start_datetime_text = tsdrdata.TSDRSingle["MetaInfoExecTSDRStartTimestamp"]
        complete_datetime_text = tsdrdata.TSDRSingle["MetaInfoExecTSDRCompleteTimestamp"]
        for text_timestamp in (start_datetime_text, complete_datetime_text):
            ts_as_datetime = datetime.fromisoformat(text_timestamp) # we convert time w/o (no ValuError)
            ts_as_text = ts_as_datetime.isoformat(timespec='microseconds') # confirm round-trip conversion okay
            self.assertEqual(text_timestamp, ts_as_text)


        


    # Test release-independent metainfo data (does not change release-to-release)
    def test_A004_check_releaseindependent_metainfo(self):
        metainfo = plumage.GetMetainfo()
        # XSLT (Plumage)
        self.assertEqual(metainfo["MetaInfoXSLTName"], "Plumage")
        self.assertEqual(metainfo["MetaInfoXSLTAuthor"], "Terry Carroll")
        self.assertEqual(metainfo["MetaInfoXSLTURL"], "https://github.com/codingatty/Plumage")
        self.assertEqual(metainfo["MetaInfoXSLTLicense"], "Apache License, version 2.0 (January 2004)")
        self.assertEqual(metainfo["MetaInfoXSLTSPDXLicenseIdentifier"], "Apache-2.0")
        self.assertEqual(metainfo["MetaInfoXSLTLicenseURL"], "http://www.apache.org/licenses/LICENSE-2.0")

        # Library (Python-py)
        self.assertEqual(metainfo["MetaInfoLibraryName"], "Plumage-py")
        self.assertEqual(metainfo["MetaInfoLibraryAuthor"], "Terry Carroll")
        self.assertEqual(metainfo["MetaInfoLibraryURL"], "https://github.com/codingatty/Plumage-py")
        self.assertEqual(metainfo["MetaInfoLibraryLicense"], "Apache License, version 2.0 (January 2004)")
        self.assertEqual(metainfo["MetaInfoLibrarySPDXLicenseIdentifier"], "Apache-2.0")
        self.assertEqual(metainfo["MetaInfoLibraryLicenseURL"], "http://www.apache.org/licenses/LICENSE-2.0")

    # Test release-dependent metainfo data (changes, or may change, from release-to-release)
    def test_A005_check_releasedependent_metainfo(self):
        metainfo = plumage.GetMetainfo()

        # XSLT (Plumage)
        self.assertEqual(metainfo["MetaInfoXSLTVersion"], "1.4.0-pre")
        self.assertEqual(metainfo["MetaInfoXSLTDate"], "2020-10-03")
        self.assertEqual(metainfo["MetaInfoXSLTCopyright"], "Copyright 2014-2020 Terry Carroll")

        # Library (Python-py)
        self.assertEqual(metainfo["MetaInfoLibraryVersion"], "1.4.0-pre")
        self.assertEqual(metainfo["MetaInfoLibraryDate"], "2020-10-03")
        self.assertEqual(metainfo["MetaInfoLibraryCopyright"], "Copyright 2014-2020 Terry Carroll")

    # Test metainfo consistency
    def test_A006_check_metainfo_consistency(self):
        '''
         1. All keys from GetMetainfo() are also in run-time TSDR data (both ST.66 and ST.96)
         2. All values from GetMetainfo() match those from run-time TSDR data (both ST.66 and ST.96)
        '''
        metainfo = plumage.GetMetainfo()

        t66 = plumage.TSDRReq()
        testfile = os.path.join(self.TESTFILES_DIR, "sn76044902-ST66.xml")
        t66.getTSDRInfo(testfile)

        t96 = plumage.TSDRReq()
        testfile = os.path.join(self.TESTFILES_DIR, "sn76044902-ST96.xml")
        t96.getTSDRInfo(testfile)

        # all keys line up with st.66 and st.96 keys
        self.assertTrue(set(metainfo).issubset(set(t66.TSDRData.TSDRSingle)))
        self.assertTrue(set(metainfo).issubset(set(t96.TSDRData.TSDRSingle)))

        # all values line up with st.66 
        for K in metainfo:
            self.assertEqual(metainfo[K], t66.TSDRData.TSDRSingle[K])

        # all values line up with st.96 
        for K in metainfo:
            self.assertEqual(metainfo[K], t96.TSDRData.TSDRSingle[K])

    # Group B
    # Test XML fetch only, unzipped XML
    def test_B001_step_by_step_thru_xml_unzipped(self):
        t = plumage.TSDRReq()
        self.assertFalse(t.XMLDataIsValid)
        self.assertFalse(t.CSVDataIsValid)
        self.assertFalse(t.TSDRData.TSDRMapIsValid)
        testfile = os.path.join(self.TESTFILES_DIR, "sn76044902-ST66.xml")
        t.getXMLData(testfile)
        self.assertTrue(t.XMLDataIsValid)
        self.assertFalse(t.CSVDataIsValid)
        self.assertFalse(t.TSDRData.TSDRMapIsValid)

    # Test XML fetch only, zipped
    def test_B002_step_by_step_thru_xml_zipped(self):
        t = plumage.TSDRReq()
        self.assertFalse(t.XMLDataIsValid)
        self.assertFalse(t.CSVDataIsValid)
        self.assertFalse(t.TSDRData.TSDRMapIsValid)
        testfile = os.path.join(self.TESTFILES_DIR, "sn76044902.zip")
        t.getXMLData(testfile)
        self.assertTrue(t.XMLDataIsValid)
        self.assertFalse(t.CSVDataIsValid)
        self.assertFalse(t.TSDRData.TSDRMapIsValid)
        
    # Group C
    # Test through CSV creation, unzipped XML
    def test_C001_step_by_step_thru_csv_unzipped(self):
        t = plumage.TSDRReq()
        self.assertFalse(t.XMLDataIsValid)
        self.assertFalse(t.CSVDataIsValid)
        self.assertFalse(t.TSDRData.TSDRMapIsValid)
        testfile = os.path.join(self.TESTFILES_DIR, "sn76044902-ST66.xml")
        t.getXMLData(testfile)
        self.assertTrue(t.XMLDataIsValid)
        self.assertFalse(t.CSVDataIsValid)
        self.assertFalse(t.TSDRData.TSDRMapIsValid)
        t.getCSVData()
        self.assertTrue(t.XMLDataIsValid)
        self.assertTrue(t.CSVDataIsValid)
        self.assertFalse(t.TSDRData.TSDRMapIsValid)

    # Test through CSV creation, zipped
    def test_C002_step_by_step_thru_csv_zipped(self):
        t = plumage.TSDRReq()
        self.assertFalse(t.XMLDataIsValid)
        self.assertFalse(t.CSVDataIsValid)
        self.assertFalse(t.TSDRData.TSDRMapIsValid)
        testfile = os.path.join(self.TESTFILES_DIR, "sn76044902.zip")
        t.getXMLData(testfile)
        self.assertTrue(t.XMLDataIsValid)
        self.assertFalse(t.CSVDataIsValid)
        self.assertFalse(t.TSDRData.TSDRMapIsValid)
        t.getCSVData()
        self.assertTrue(t.XMLDataIsValid)
        self.assertTrue(t.CSVDataIsValid)
        self.assertFalse(t.TSDRData.TSDRMapIsValid)
       
    # Group D
    # Test all the way through TSDR map
    def test_D001_step_by_step_thru_map(self):
        t = plumage.TSDRReq()
        self.assertFalse(t.XMLDataIsValid)
        self.assertFalse(t.CSVDataIsValid)
        self.assertFalse(t.TSDRData.TSDRMapIsValid)
        testfile = os.path.join(self.TESTFILES_DIR, "sn76044902.zip")
        t.getXMLData(testfile)
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

    # Group E
    # Test parameter validations
    def test_E001_no_such_file(self):
        t = plumage.TSDRReq()
        self.assertRaises(IOError, t.getTSDRInfo, "filedoesnotexist.zip")

    def test_E002_getTSDRInfo_parameter_validation(self):
        t = plumage.TSDRReq()
        self.assertRaises(ValueError, t.getTSDRInfo, "123456789", "s") # > 8-digit serial no.
        plumage.TSDRReq._prior_TSDR_call_time = TestUM.INITIAL_PRIOR_TSDR_CALL_TIME  # reset already-called flag after each call to avoid delays in test
        self.assertRaises(ValueError, t.getTSDRInfo, "1234567", "s")   # < 8-digit serial no.
        plumage.TSDRReq._prior_TSDR_call_time = TestUM.INITIAL_PRIOR_TSDR_CALL_TIME 
        self.assertRaises(ValueError, t.getTSDRInfo, 123456789, "s")   # non-character serial no.
        plumage.TSDRReq._prior_TSDR_call_time = TestUM.INITIAL_PRIOR_TSDR_CALL_TIME 
        self.assertRaises(ValueError, t.getTSDRInfo, "1234567Z", "s")  # non-numeric serial no.
        plumage.TSDRReq._prior_TSDR_call_time = TestUM.INITIAL_PRIOR_TSDR_CALL_TIME 
        self.assertRaises(ValueError, t.getTSDRInfo, "12345678", "r")  # > 7-digit reg. no
        plumage.TSDRReq._prior_TSDR_call_time = TestUM.INITIAL_PRIOR_TSDR_CALL_TIME 
        self.assertRaises(ValueError, t.getTSDRInfo, "123456", "r")    # < 7-digit reg. no
        plumage.TSDRReq._prior_TSDR_call_time = TestUM.INITIAL_PRIOR_TSDR_CALL_TIME 
        self.assertRaises(ValueError, t.getTSDRInfo, 23456, "r")       # non-character reg. no
        plumage.TSDRReq._prior_TSDR_call_time = TestUM.INITIAL_PRIOR_TSDR_CALL_TIME 
        self.assertRaises(ValueError, t.getTSDRInfo, "123456Z", "r")   # non-numeric reg. no
        plumage.TSDRReq._prior_TSDR_call_time = TestUM.INITIAL_PRIOR_TSDR_CALL_TIME 
        self.assertRaises(ValueError, t.getTSDRInfo, "123456", "X")    # incorrect type (not "s"/"r")

    # Group F
    # XML/XSL variations
    
    def test_F001_flag_ST961D3(self):
        '''
        Plumage recognizes ST.96 1_D3 format XML, but no longer supports
        '''
        t = plumage.TSDRReq()
        testfile = os.path.join(self.TESTFILES_DIR, "rn2178784-ST-961_D3.xml")
        t.getTSDRInfo(testfile)
        self.assertTrue(t.XMLDataIsValid)
        self.assertFalse(t.CSVDataIsValid)
        self.assertFalse(t.TSDRData.TSDRMapIsValid)
        self.assertEqual(t.ErrorCode,"CSV-UnsupportedXML")
        
    def test_F002_process_ST961D3(self):
        '''
        test using an alternate XSL file.
        In this case, rn2178784-ST-961_D3.xml is a file formatted under 
        the old ST.96 format, no longer used by the PTO; ST96-V1.0.1.xsl 
        is an XSLT file that used to support that format
        '''
        t = plumage.TSDRReq()
        testxsl = os.path.join(self.TESTFILES_DIR, "ST96-V1.0.1.xsl")
        with open(testxsl) as f:
            ST961D3xslt = f.read()
        t.setXSLT(ST961D3xslt)
        testfile = os.path.join(self.TESTFILES_DIR, "rn2178784-ST-961_D3.xml")
        t.getTSDRInfo(testfile)
        self.assertTrue(t.TSDRData.TSDRMapIsValid)
        
    def test_F003_confirm_ST96_support_201605(self):
        '''
        In May 2016, the USPTO switched from ST96 V1_D3 to ST96 2.2.1.
        This test is to ensure that Plumage provides identical result
        under both the the old and new formats. 
        '''
        #old:
        t_old = plumage.TSDRReq()
        testxsl = os.path.join(self.TESTFILES_DIR, "ST96-V1.0.1.xsl")
        with open(testxsl) as f:
            ST961D3xslt = f.read()
        t_old.setXSLT(ST961D3xslt)
        testfile = os.path.join(self.TESTFILES_DIR, "rn2178784-ST-961_D3.xml")
        t_old.getTSDRInfo(testfile)
        plumage.TSDRReq._prior_TSDR_call_time = TestUM.INITIAL_PRIOR_TSDR_CALL_TIME  # reset already-called flag after each call to avoid delays in test
        #ignore the DiagnosticInfo... keys; they are expected to differ
        t_old_keys = set([x for x in t_old.TSDRData.TSDRSingle.keys() if not x.startswith("DiagnosticInfo")])

        #new:
        t_new = plumage.TSDRReq()
        testfile = os.path.join(self.TESTFILES_DIR, "rn2178784-ST-962.2.1.xml")
        t_new.getTSDRInfo(testfile)
        plumage.TSDRReq._prior_TSDR_call_time = TestUM.INITIAL_PRIOR_TSDR_CALL_TIME  # reset already-called flag after each call to avoid delays in test
        t_new_keys = set([x for x in t_new.TSDRData.TSDRSingle.keys() if 
            not x.startswith("DiagnosticInfo") and 
            not x.startswith("MetaInfo")])

        # Same keys in both
        self.assertEqual(t_new_keys, t_old_keys)
        # and same values
        for key in t_new_keys:
            self.assertEqual(t_new.TSDRData.TSDRSingle[key], t_old.TSDRData.TSDRSingle[key], key)

        # Confirm the TSDRMultis match, too
        # (No "Diagnostic..." entries to filter out)
        for listkey in t_old.TSDRData.TSDRMulti.keys():
            self.assertEqual(t_new.TSDRData.TSDRMulti[listkey],
                             t_old.TSDRData.TSDRMulti[listkey])

    def test_F004_process_with_alternate_XSL(self):
        '''
        Process alternate XSL.
        Pull out nothing but application no. and publication date
        '''
        testxsl = os.path.join(self.TESTFILES_DIR, "appno+pubdate.xsl")
        with open(testxsl) as f:
            altXSL = f.read()
        t = plumage.TSDRReq()
        t.setXSLT(altXSL)
        testfile = os.path.join(self.TESTFILES_DIR, "sn76044902.zip")
        t.getTSDRInfo(testfile)
        self.assertTrue(t.XMLDataIsValid)
        self.assertTrue(t.CSVDataIsValid)
        self.assertTrue(t.TSDRData.TSDRMapIsValid)
        
    def test_F005_process_with_alternate_XSL_inline(self):
        '''
        Process alternate XSL, placed inline
        Pull out nothing but application no. and publication date.
        Other than placing the XSL inline, this is identical to 
        Test_F004_process_with_alternate_XSL

        Note: using inline is not recommended; XSL processor is picky and inline
        XSL is hard to debug. The recommended approach is to use an external file
        and develop/debug the XSL separately, using an external XSL processor such
        as MSXSL or equivalent.
        '''

        altXSL = '''
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tm="http://www.wipo.int/standards/XMLSchema/trademarks" xmlns:pto="urn:us:gov:doc:uspto:trademark:status">
<xsl:output method="text" encoding="utf-8"/>
<xsl:template match="tm:Transaction">
<xsl:apply-templates select=".//tm:TradeMark"/>
</xsl:template>
<xsl:template match="tm:TradeMark">
<xsl:text/>ApplicationNumber,"<xsl:value-of select="tm:ApplicationNumber"/>"<xsl:text/>
PublicationDate,"<xsl:value-of select="tm:PublicationDetails/tm:Publication/tm:PublicationDate"/>"<xsl:text/>
</xsl:template>
</xsl:stylesheet>
        '''
        t = plumage.TSDRReq()
        t.setXSLT(altXSL)
        testfile = os.path.join(self.TESTFILES_DIR, "sn76044902.zip")
        t.getTSDRInfo(testfile)
        self.assertTrue(t.XMLDataIsValid)
        self.assertTrue(t.CSVDataIsValid)
        self.assertTrue(t.TSDRData.TSDRMapIsValid)

    # Group G
    # XSL/CSV validations
    
    def _interior_test_with_XSLT_override(self, xsl_text, success_expected=True):
        '''
        Interior test for each call
        '''
        
        t = plumage.TSDRReq()
        plumage.TSDRReq._prior_TSDR_call_time = TestUM.INITIAL_PRIOR_TSDR_CALL_TIME  # reset already-called flag after each call to avoid delays in test
        t.setXSLT(xsl_text)
        testfile = os.path.join(self.TESTFILES_DIR, "sn76044902.zip")
        t.getXMLData(testfile)
        t.getCSVData()
        if success_expected:
            self.assertTrue(t.CSVDataIsValid)
            t.getTSDRData()
            self.assertTrue(t.TSDRData.TSDRMapIsValid)
        else:
            self.assertFalse(t.CSVDataIsValid)
        return t
    
    def test_G001_XSLT_with_blanks(self):
        '''
        Process alternate XSL, slightly malformed to generate empty lines;
        make sure they're ignored (new feature in Plumage 1.2)
        '''
        testskeleton = os.path.join(self.TESTFILES_DIR, "xsl_exception_test_skeleton.txt")
        with open(testskeleton) as f:
            XSL_skeleton = f.read()
        XSLGUTS = "XSLGUTS\n" 
        XSL_text_tag = '<xsl:text/>'
        XSL_appno = 'ApplicationNumber,"<xsl:value-of select="tm:ApplicationNumber"/>"<xsl:text/>\n'
        XSL_pubdate = 'PublicationDate,"<xsl:value-of select="tm:PublicationDetails/tm:Publication/tm:PublicationDate"/>"<xsl:text/>\n'
        XSL_two_blanklines = '   \n     \n'
        XSL_one_blankline = '   \n'

        # First, try a vanilla working version
        new_guts = XSL_text_tag + XSL_appno + XSL_pubdate
        altXSL = XSL_skeleton.replace(XSLGUTS, new_guts)
        t = self._interior_test_with_XSLT_override(altXSL, success_expected=True)
        normal_CSV_length = len(t.CSVData)

        # now the variations; should be ignored and get same result

        #blank lines at end
        new_guts = XSL_text_tag + XSL_appno + XSL_pubdate + XSL_two_blanklines
        altXSL = XSL_skeleton.replace(XSLGUTS, new_guts)
        t = self._interior_test_with_XSLT_override(altXSL, success_expected=True)
        self.assertEqual(len(t.CSVData), normal_CSV_length)

        #blank lines at beginning
        new_guts = XSL_text_tag + XSL_two_blanklines + XSL_appno + XSL_pubdate 
        altXSL = XSL_skeleton.replace(XSLGUTS, new_guts)
        t = self._interior_test_with_XSLT_override(altXSL, success_expected=True)
        self.assertEqual(len(t.CSVData), normal_CSV_length)

    def test_G002_CSV_too_short(self):
        '''
        Sanity check requires at least two non-blank lines (at least two fields) in CSV.
        '''

        testskeleton = os.path.join(self.TESTFILES_DIR, "xsl_exception_test_skeleton.txt")
        with open(testskeleton) as f:
            XSL_skeleton = f.read()
        XSLGUTS = "XSLGUTS\n" 
        XSL_text_tag = '<xsl:text/>'
        XSL_appno = 'ApplicationNumber,"<xsl:value-of select="tm:ApplicationNumber"/>"<xsl:text/>\n'
        XSL_pubdate = 'PublicationDate,"<xsl:value-of select="tm:PublicationDetails/tm:Publication/tm:PublicationDate"/>"<xsl:text/>\n'
        XSL_two_blanklines = '   \n     \n'
        XSL_one_blankline = '   \n'

        # First, try a vanilla working version, 2 fields, appno and publication date
        new_guts = XSL_appno + XSL_pubdate
        altXSL = XSL_skeleton.replace(XSLGUTS, new_guts)
        t = self._interior_test_with_XSLT_override(altXSL, success_expected=True)
        normal_CSV_length = len(t.CSVData)

        # Now, application no. only, publication date only; each should fail
        new_guts = XSL_appno
        altXSL = XSL_skeleton.replace(XSLGUTS, new_guts)
        t = self._interior_test_with_XSLT_override(altXSL, success_expected=False)
        self.assertEqual(t.ErrorCode, "CSV-ShortCSV")
        new_guts = XSL_pubdate
        altXSL = XSL_skeleton.replace(XSLGUTS, new_guts)
        t = self._interior_test_with_XSLT_override(altXSL, success_expected=False)
        self.assertEqual(t.ErrorCode, "CSV-ShortCSV")

        # Also fails even if >2 lines, but all but 1 is blank
        new_guts = XSL_appno + XSL_two_blanklines
        altXSL = XSL_skeleton.replace(XSLGUTS, new_guts)
        t = self._interior_test_with_XSLT_override(altXSL, success_expected=False)
        self.assertEqual(t.ErrorCode, "CSV-ShortCSV")

    def test_G003_CSV_malformed(self):
        '''
        Test common malforms of CSVs get caught
        '''

        testskeleton = os.path.join(self.TESTFILES_DIR, "xsl_exception_test_skeleton.txt")
        with open(testskeleton) as f:
            XSL_skeleton = f.read()
        XSLGUTS = "XSLGUTS\n" 
        XSL_text_tag = '<xsl:text/>'
        XSL_appno = 'ApplicationNumber,"<xsl:value-of select="tm:ApplicationNumber"/>"<xsl:text/>\n'
        XSL_pubdate = 'PublicationDate,"<xsl:value-of select="tm:PublicationDetails/tm:Publication/tm:PublicationDate"/>"<xsl:text/>\n'
        XSL_two_blanklines = '   \n     \n'
        XSL_one_blankline = '   \n'

        # No good: missing comma (space instead)
        XSL_appno_bad = 'ApplicationNumber "<xsl:value-of select="tm:ApplicationNumber"/>"<xsl:text/>\n'
        new_guts = XSL_appno_bad + XSL_pubdate
        altXSL = XSL_skeleton.replace(XSLGUTS, new_guts)
        t = self._interior_test_with_XSLT_override(altXSL, success_expected=False)
        self.assertEqual(t.ErrorCode, "CSV-InvalidKeyValuePair")

        # No good: missing comma (no separator)
        XSL_appno_bad = 'ApplicationNumber"<xsl:value-of select="tm:ApplicationNumber"/>"<xsl:text/>\n'
        new_guts = XSL_appno_bad + XSL_pubdate
        altXSL = XSL_skeleton.replace(XSLGUTS, new_guts)
        t = self._interior_test_with_XSLT_override(altXSL, success_expected=False)
        self.assertEqual(t.ErrorCode, "CSV-InvalidKeyValuePair")

        # No good: missing quotes
        XSL_appno_bad = 'ApplicationNumber,<xsl:value-of select="tm:ApplicationNumber"/><xsl:text/>\n'
        new_guts = XSL_appno_bad + XSL_pubdate
        altXSL = XSL_skeleton.replace(XSLGUTS, new_guts)
        t = self._interior_test_with_XSLT_override(altXSL, success_expected=False)
        self.assertEqual(t.ErrorCode, "CSV-InvalidValue")

        # No good: missing close-quote
        XSL_appno_bad = 'ApplicationNumber,"<xsl:value-of select="tm:ApplicationNumber"/><xsl:text/>\n'
        new_guts = XSL_appno_bad + XSL_pubdate
        altXSL = XSL_skeleton.replace(XSLGUTS, new_guts)
        t = self._interior_test_with_XSLT_override(altXSL, success_expected=False)
        self.assertEqual(t.ErrorCode, "CSV-InvalidValue")

        # No good: missing open-quote
        XSL_appno_bad = 'ApplicationNumber,<xsl:value-of select="tm:ApplicationNumber"/>"<xsl:text/>\n'
        new_guts = XSL_appno_bad + XSL_pubdate
        altXSL = XSL_skeleton.replace(XSLGUTS, new_guts)
        t = self._interior_test_with_XSLT_override(altXSL, success_expected=False)
        self.assertEqual(t.ErrorCode, "CSV-InvalidValue")

        # No good: space between key and field after comma
        XSL_appno_bad = 'ApplicationNumber, "<xsl:value-of select="tm:ApplicationNumber"/>"<xsl:text/>\n'
        new_guts = XSL_appno_bad + XSL_pubdate
        altXSL = XSL_skeleton.replace(XSLGUTS, new_guts)
        t = self._interior_test_with_XSLT_override(altXSL, success_expected=False)
        self.assertEqual(t.ErrorCode, "CSV-InvalidValue")

        # No good: space in key name (space instead)
        XSL_appno_bad = 'Application Number,"<xsl:value-of select="tm:ApplicationNumber"/>"<xsl:text/>\n'
        new_guts = XSL_appno_bad + XSL_pubdate
        altXSL = XSL_skeleton.replace(XSLGUTS, new_guts)
        t = self._interior_test_with_XSLT_override(altXSL, success_expected=False)
        self.assertEqual(t.ErrorCode, "CSV-InvalidKey")

        # No good: disallowed character '-' in key name
        XSL_appno_bad = 'Application-Number,"<xsl:value-of select="tm:ApplicationNumber"/>"<xsl:text/>\n'
        new_guts = XSL_appno_bad + XSL_pubdate
        altXSL = XSL_skeleton.replace(XSLGUTS, new_guts)
        t = self._interior_test_with_XSLT_override(altXSL, success_expected=False)
        self.assertEqual(t.ErrorCode, "CSV-InvalidKey")

        # No good: leading blank 
        XSL_appno_bad = ' ApplicationNumber,"<xsl:value-of select="tm:ApplicationNumber"/>"<xsl:text/>\n'
        new_guts = XSL_appno_bad + XSL_pubdate
        altXSL = XSL_skeleton.replace(XSLGUTS, new_guts)
        t = self._interior_test_with_XSLT_override(altXSL, success_expected=False)
        self.assertEqual(t.ErrorCode, "CSV-InvalidKey")

        # No good: trailing blank 
        XSL_appno_bad = 'ApplicationNumber,"<xsl:value-of select="tm:ApplicationNumber"/>" <xsl:text/>\n'
        new_guts = XSL_appno_bad + XSL_pubdate
        altXSL = XSL_skeleton.replace(XSLGUTS, new_guts)
        t = self._interior_test_with_XSLT_override(altXSL, success_expected=False)
        self.assertEqual(t.ErrorCode, "CSV-InvalidValue")

    # Group H
    # support for additional fields
    
    def test_H001_verify_class_fields_exist(self):
        '''
        Make sure the three new dicts added to support trademark classifications:
          InternationalClassDescriptionList
          DomesticClassDescriptionList
          FirstUseDatesList
        are present for both ST.66 and ST.96 formats.
        '''
        t66 = plumage.TSDRReq()
        testfile = os.path.join(self.TESTFILES_DIR, "sn76044902-ST66.xml")
        t66.getTSDRInfo(testfile)
        plumage.TSDRReq._prior_TSDR_call_time = TestUM.INITIAL_PRIOR_TSDR_CALL_TIME  # reset already-called flag after each call to avoid delays in test
        t96 = plumage.TSDRReq()
        testfile = os.path.join(self.TESTFILES_DIR, "sn76044902-ST96.xml")
        t96.getTSDRInfo(testfile)
        self.assertTrue("InternationalClassDescriptionList" in t66.TSDRData.TSDRMulti)
        self.assertTrue("DomesticClassDescriptionList" in t66.TSDRData.TSDRMulti)
        self.assertTrue("FirstUseDatesList" in t66.TSDRData.TSDRMulti)
        self.assertTrue("InternationalClassDescriptionList" in t96.TSDRData.TSDRMulti)
        self.assertTrue("DomesticClassDescriptionList" in t96.TSDRData.TSDRMulti)
        self.assertTrue("FirstUseDatesList" in t96.TSDRData.TSDRMulti)
        
    def test_H002_verify_intl_class_consistency(self):
        '''
        Make sure that all international classes are reported consistently and correctly
          InternationalClassDescriptionList / InternationalClassNumber (both formats)
          DomesticClassDescriptionList / PrimaryClassNumber (both formats)
          DomesticClassDescriptionList / NiceClassNumber (ST.96 only)
          FirstUseDatesList / PrimaryClassNumber (both formats)

        For the test cases, each of these should have the same set of class IDs: ["009", "042"], although maybe more than once
        '''
        t66 = plumage.TSDRReq()
        testfile = os.path.join(self.TESTFILES_DIR, "sn76044902-ST66.xml")
        t66.getTSDRInfo(testfile)
        plumage.TSDRReq._prior_TSDR_call_time = TestUM.INITIAL_PRIOR_TSDR_CALL_TIME  # reset already-called flag after each call to avoid delays in test
        tsdrmulti = t66.TSDRData.TSDRMulti
        ICD_list = tsdrmulti["InternationalClassDescriptionList"]
        ST66_IC_nos = [entry["InternationalClassNumber"] for entry in ICD_list]
        DCD_list = tsdrmulti["DomesticClassDescriptionList"]
        ST66_DCD_PrimaryClass_nos = [entry["PrimaryClassNumber"] for entry in DCD_list]
        FUD_list = tsdrmulti["FirstUseDatesList"]
        ST66_FUD_PrimaryClass_nos = [entry["PrimaryClassNumber"] for entry in FUD_list]
        t96 = plumage.TSDRReq()
        testfile = os.path.join(self.TESTFILES_DIR, "sn76044902-ST96.xml")
        t96.getTSDRInfo(testfile)
        tsdrmulti = t96.TSDRData.TSDRMulti
        ICD_list = tsdrmulti["InternationalClassDescriptionList"]
        ST96_IC_nos = [entry["InternationalClassNumber"] for entry in ICD_list]
        DCD_list = tsdrmulti["DomesticClassDescriptionList"]
        ST96_DCD_PrimaryClass_nos = [entry["PrimaryClassNumber"] for entry in DCD_list]
        ST96_DCD_NiceClass_nos = [entry["NiceClassNumber"] for entry in DCD_list]
        FUD_list = tsdrmulti["FirstUseDatesList"]
        ST96_FUD_PrimaryClass_nos = [entry["PrimaryClassNumber"] for entry in FUD_list]
        # All of these should be the class nos "009" and "042", although possibly multiple times
        control_set = set(["009", "042"])
        self.assertEqual(control_set, set(ST66_IC_nos))
        self.assertEqual(control_set, set(ST96_IC_nos))
        self.assertEqual(control_set, set(ST66_DCD_PrimaryClass_nos))
        self.assertEqual(control_set, set(ST96_DCD_PrimaryClass_nos))
        self.assertEqual(control_set, set(ST96_DCD_NiceClass_nos)) # No ST.66 equivalent
        self.assertEqual(control_set, set(ST66_FUD_PrimaryClass_nos))
        self.assertEqual(control_set, set(ST96_FUD_PrimaryClass_nos))
  
# Group I
    # tests for new features

    # TODO: This is testing how long one call takes, which is not necessarily time since last call
    #       As a result, tests sometimes falsely fail
    def execute_one_timed_call(self, fake_delay=None):
        '''
        Fake delay is the amount of time, in seconds, to delay before calling
        '''
        starting_time = datetime.now()
        t = plumage.TSDRReq()
        testfile = os.path.join(self.TESTFILES_DIR, "sn76044902.zip")
        if fake_delay is not None: # optionally fake time delay in workload
            time.sleep(fake_delay)

        t.getTSDRInfo(testfile)
        ending_time = datetime.now()
        self.assertTrue(t.TSDRData.TSDRMapIsValid)
        total_time_in_ms = (ending_time-starting_time)/timedelta(milliseconds=1)
        return total_time_in_ms

    def test_I001_default_delay(self):
        '''
        Test to make sure data calls are delayed to keep from looking like a denial-of-service attack against PTO

        Note: testing timing is fraught with uncertainty, but assuming a local file read is more or less instantaneous,
        this shouldn't be too bad, at least within the 100-milisecond range used here
        '''

        TOLERANCE = 100   # 100 ms
        #default_delay = 1 # default 1-second delay

        # First run should be almost instantaneous:
        total_time_in_ms = self.execute_one_timed_call()
        self.assertAlmostEqual(total_time_in_ms, 0, delta=TOLERANCE)

        # But second run should be delayed about a second (1000 ms)
        total_time_in_ms = self.execute_one_timed_call()
        self.assertGreater(total_time_in_ms, 1000)                         # more than one second
        self.assertAlmostEqual(total_time_in_ms, 1000, delta=TOLERANCE)    # but not that much more! (i.e < 1.1 sec)

    def test_I002_default_delay_with_faked_workload(self):
        '''
        This test ensures that there are no pointless delays, if processing itself is already taking time.
        For example, if we want at least a one-second between calls to TSDR, and processing the info itself 
        takes more than one second, there should be no added delay at all.
        '''
        TOLERANCE = 100   # 100 ms

        # First run should be almost instantaneous:
        total_time_in_ms = self.execute_one_timed_call()
        self.assertAlmostEqual(total_time_in_ms, 0, delta=TOLERANCE)

        # Second run, pretend it takes 1.2 seconds of work between calls 
        total_time_in_ms = self.execute_one_timed_call(fake_delay=1.2)
        self.assertGreater(total_time_in_ms, 1000)                         # is required to be more than one second
        self.assertAlmostEqual(total_time_in_ms, 1200, delta=TOLERANCE)    # but not much more than the 1.2 seconds we already should get "credit" for

    def test_I003_zero_delay(self):
        '''
        This test ensures we can override the delay if we want
        '''
        TOLERANCE = 100   # 100 ms

        plumage.SetIntervalTime(0)
        # First run should be almost instantaneous, as usual:
        total_time_in_ms = self.execute_one_timed_call()
        self.assertAlmostEqual(total_time_in_ms, 0, delta=TOLERANCE)

        # Subsequent runs should also now be almost instantaneous with the override 
        total_time_in_ms = self.execute_one_timed_call()
        self.assertAlmostEqual(total_time_in_ms, 0, delta=TOLERANCE)
        total_time_in_ms = self.execute_one_timed_call()
        self.assertAlmostEqual(total_time_in_ms, 0, delta=TOLERANCE)
        total_time_in_ms = self.execute_one_timed_call()
        self.assertAlmostEqual(total_time_in_ms, 0, delta=TOLERANCE)

        # go back to default, and we should get one-second delays again
        plumage.ResetIntervalTime()
        total_time_in_ms = self.execute_one_timed_call()
        self.assertGreater(total_time_in_ms, 1000)                
        self.assertAlmostEqual(total_time_in_ms, 1000, delta=TOLERANCE)
        total_time_in_ms = self.execute_one_timed_call()
        self.assertGreater(total_time_in_ms, 1000)                
        self.assertAlmostEqual(total_time_in_ms, 1000, delta=TOLERANCE)

    def test_I004_fractional_delay(self):
        '''
        Verify a non-integer number of seconds works as expected
        '''

        TOLERANCE = 100   # 100 ms
        #default_delay = 1 # default 1-second delay

        plumage.SetIntervalTime(1.5)  # 1.5-second interval
        # First run should be almost instantaneous, as usual:
        total_time_in_ms = self.execute_one_timed_call()
        self.assertAlmostEqual(total_time_in_ms, 0, delta=TOLERANCE)

        # But second run should be delayed about 1.5 seconds (1500 ms)
        total_time_in_ms = self.execute_one_timed_call()
        self.assertGreater(total_time_in_ms, 1500)                         
        self.assertAlmostEqual(total_time_in_ms, 1500, delta=TOLERANCE)  

    def test_I005_negative_delay(self):
        '''
        a negative delay will not let you time travel, but guaranteeing an interval of at 
        least a negative number of seconds is just like saying zero
        '''

        TOLERANCE = 100   # 100 ms
        #default_delay = 1 # default 1-second delay

        plumage.SetIntervalTime(-10)  # negative ten-second interval
        # First run should be almost instantaneous, as usual:
        total_time_in_ms = self.execute_one_timed_call()
        self.assertAlmostEqual(total_time_in_ms, 0, delta=TOLERANCE)

        # and so should subsequent runs  
        total_time_in_ms = self.execute_one_timed_call()
        self.assertAlmostEqual(total_time_in_ms, 0, delta=TOLERANCE)
        total_time_in_ms = self.execute_one_timed_call()
        self.assertAlmostEqual(total_time_in_ms, 0, delta=TOLERANCE)
        total_time_in_ms = self.execute_one_timed_call()
        self.assertAlmostEqual(total_time_in_ms, 0, delta=TOLERANCE)

    def test_I006_nonnumeric_delay(self):
        '''
        Non-numerics should raise TypeError
        '''

        self.assertRaises(TypeError, plumage.SetIntervalTime, "1")
        self.assertRaises(TypeError, plumage.SetIntervalTime, None)

        # so should a missing operand
        self.assertRaises(TypeError, plumage.SetIntervalTime)


if __name__ == '__main__':
    unittest.main(verbosity=2)
