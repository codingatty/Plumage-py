#! python2
import unittest
import os.path
from datetime import datetime

from Plumage import plumage

class TestUM(unittest.TestCase):
    '''
    Not actually a functional test;
    a final checklist to ensure dates and release info are correctly updated in
    source before release
    '''

    TESTFILES_DIR = "testfiles\\"

    def setUp(self):
        t = plumage.TSDRReq()
        t.getTSDRInfo(self.TESTFILES_DIR+"sn76044902.zip")
        self.assertTrue(t.TSDRData.TSDRMapIsValid)
        self.tsdr_single = t.TSDRData.TSDRSingle
        plumage_dir = os.path.dirname(plumage.__file__)
        plumage_source_path = plumage_dir + "\\plumage.py"
        self.modification_timestamp = os.path.getmtime(plumage_source_path)

    def test_001_releaseno(self):
        self.assertEqual(self.tsdr_single["DiagnosticInfoImplementationVersion"], "1.2.0")

    def test_002_modificationdate(self):
        modification_date = datetime.fromtimestamp(self.modification_timestamp).strftime("%Y-%m-%d")
        self.assertEqual(self.tsdr_single["DiagnosticInfoImplementationDate"], modification_date)
        
    def test_003_copyrightnotice(self):
        modification_year = datetime.fromtimestamp(self.modification_timestamp).strftime("%Y")
        copyright_range = "2014-" + modification_year
        self.assertTrue(copyright_range in self.tsdr_single["DiagnosticInfoImplementationCopyright"])

if __name__ == '__main__':
    unittest.main(verbosity=5)