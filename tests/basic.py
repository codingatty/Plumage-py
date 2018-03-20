import unittest
from testing_context import plumage

class TestUM(unittest.TestCase):

    TESTFILES_DIR = "testfiles\\"
 
    def setUp(self):
        pass

    def test_A001_test_initialize(self):
        '''
        Simple test, just verify TSDRReq can be initialized correctly
        '''
        t = plumage.TSDRReq()
        self.assertFalse(t.XMLDataIsValid)
        self.assertFalse(t.CSVDataIsValid)
        self.assertFalse(t.TSDRData.TSDRMapIsValid)

if __name__ == '__main__':
    unittest.main(verbosity=5)