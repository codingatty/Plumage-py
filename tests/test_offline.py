import os
import sys
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

    # Group O (in test_online.py): Online tests that actually hit the PTO TSDR system

    TESTFILES_DIR = "testfiles"
 
    def setUp(self):
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
        self.assertEqual(tsdrdata.TSDRSingle["DiagnosticInfoXSLTFormat"], "ST.66")
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
        if PYTHON2: # method renamed from assertRegexpMatches to assertRegex between Py2 and Py3
            self.assertRegexpMatches(tsdrdata.TSDRSingle["DiagnosticInfoImplementationVersion"],
                         r"^\d+\.\d+\.\d+(-(\w+))*$")
        if PYTHON3:
            self.assertRegex(tsdrdata.TSDRSingle["DiagnosticInfoImplementationVersion"],
                         r"^\d+\.\d+\.\d+(-(\w+))*$")
        # r"^\d+\.\d+\.\d+(-(\w+))*$"  :
        #   matches release number in the form "1.2.3", with an optional dashed suffix like "-prelease"
        self.assertEqual(tsdrdata.TSDRSingle["DiagnosticInfoImplementationLicenseURL"],
                         "http://www.apache.org/licenses/LICENSE-2.0")
        self.assertEqual(tsdrdata.TSDRSingle["DiagnosticInfoImplementationLicense"],
                         "Apache License, version 2.0 (January 2004)")
        self.assertEqual(tsdrdata.TSDRSingle["DiagnosticInfoImplementationName"],
                         "Plumage-py")
        self.assertEqual(tsdrdata.TSDRSingle["DiagnosticInfoImplementationSPDXLicenseIdentifier"],
                         "Apache-2.0")

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
        self.assertRaises(ValueError, t.getTSDRInfo, "1234567", "s")   # < 8-digit serial no.
        self.assertRaises(ValueError, t.getTSDRInfo, 123456789, "s")   # non-character serial no.
        self.assertRaises(ValueError, t.getTSDRInfo, "1234567Z", "s")  # non-numeric serial no.
        self.assertRaises(ValueError, t.getTSDRInfo, "12345678", "r")  # > 7-digit reg. no
        self.assertRaises(ValueError, t.getTSDRInfo, "123456", "r")    # < 7-digit reg. no
        self.assertRaises(ValueError, t.getTSDRInfo, 23456, "r")       # non-character reg. no
        self.assertRaises(ValueError, t.getTSDRInfo, "123456Z", "r")   # non-numeric reg. no
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
        #ignore the DiagnosticInfo... keys; they are expected to differ
        t_old_keys = set([x for x in t_old.TSDRData.TSDRSingle.keys() if not x.startswith("DiagnosticInfo")])

        #new:
        t_new = plumage.TSDRReq()
        testfile = os.path.join(self.TESTFILES_DIR, "rn2178784-ST-962.2.1.xml")
        t_new.getTSDRInfo(testfile)
        t_new_keys = set([x for x in t_new.TSDRData.TSDRSingle.keys() if not x.startswith("DiagnosticInfo")])

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
    # Feature additions
    
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
          InternationalClassDescriptionList / InternationalClassNumber
          DomesticClassDescriptionList / PrimaryClassNumber
          DomesticClassDescriptionList / NiceClassNumber (ST.96 only)
        '''
        t66 = plumage.TSDRReq()
        testfile = os.path.join(self.TESTFILES_DIR, "sn76044902-ST66.xml")
        t66.getTSDRInfo(testfile)
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
  



if __name__ == '__main__':
    unittest.main(verbosity=2)
