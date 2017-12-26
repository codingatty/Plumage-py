'''
Plumage: Python module to obtain trademark status information from USPTO's TSDR system

Version 1.2.0, 2016-03-15
Copyright 2014-2017 Terry Carroll
carroll@tjc.com

License information:

This program is licensed under Apache License, version 2.0 (January 2004);
see http://www.apache.org/licenses/LICENSE-2.0
SPX-License-Identifier: Apache-2.0

Anyone who makes use of, or who modifies, this code is encouraged
(but not required) to notify the author.
'''

import StringIO
import zipfile
import os.path
import string
import urllib2
import time
import unittest
from lxml import etree

### PEP 476 begin
try:
    import ssl
    SSL_INSTALLED = True
except ImportError:
    SSL_INSTALLED = False
### PEP 476 end

__version__ = "V. 1.2.0"
__last_updated__ = "2017-03-14"
__author__ = "Terry Carroll"
__URL__ = "https://github.com/codingatty/Plumage-py"
__copyright__ = "Copyright 2014-2017 Terry Carroll"
__license__ = "Apache License, version 2.0 (January 2004)"
__SPDX_LID__ = "Apache-2.0"
__licenseURL__ = "http://www.apache.org/licenses/LICENSE-2.0"

COMMA = ","
LINE_SEPARATOR = "\n"
WHITESPACE = string.whitespace
        
class _XSLTDescriptor(object):
    '''
    Object used to organize information relating to pre-defined XSLT transforms
      filename: name of XSLT file
      location: location (directory) of XSLT file
      pathname: full pathname of XSLT file
      transform: compiled XSLT transform
    '''

    def __init__(self, XMLformat):
        '''
        initialize a _XSLTDescriptor object for the specified transform format
        '''
        xslt_dirname = _TSDR_dirname
        xslt_filename = XMLformat+".xsl"
        xslt_pathname = os.path.join(xslt_dirname, xslt_filename)
        with open(xslt_pathname) as _f:
            _stylesheet = _f.read()
            _xslt_root = etree.XML(_stylesheet)
            transform = etree.XSLT(_xslt_root)
        self.filename = xslt_filename
        self.location = xslt_dirname
        self.pathname = xslt_pathname
        self.transform = transform

class TSDRMap(object):
    '''
    Object to hold the final results from TSDR
      TSDRSingle: dictionary of one-valued attributes; e.g.,
        registration number, application date etc.
      TSDRMulti: Lists of multi-valued attributes; e.g. assignments, events, etc
    '''

    def __init__(self):
        '''
        initialize TSDRMap object; initial state: not valid and nulls for TSDRSingle and TSDRMulti
        '''
        self.TSDRSingle = None
        self.TSDRMulti = None
        self.TSDRMapIsValid = False

_TSDR_substitutions = {
    "$XSLTFILENAME$":"Not Set",                 # XSLT stylesheet file name
    "$XSLTLOCATION$":"Not Set",                 # XSLT stylesheet location (e.g., directory pathname)
    "$IMPLEMENTATIONNAME$":"Plumage-py",        # implementation identifier
    "$IMPLEMENTATIONVERSION$":__version__,      # implementation version no.
    "$IMPLEMENTATIONDATE$":__last_updated__,    # implementation date
    "$IMPLEMENTATIONAUTHOR$":__author__,        # implementation author
    "$IMPLEMENTATIONURL$":__URL__,              # implementation URL
    "$IMPLEMENTATIONCOPYRIGHT$": __copyright__, # implementation copyright notice
    "$IMPLEMENTATIONLICENSE$":__license__,      # implementation license
    "$IMPLEMENTATIONSPDXLID$":__SPDX_LID__,     # implementation license SPDX ID
    "$IMPLEMENTATIONLICENSEURL$":__licenseURL__, #Implementation license URL
    "$EXECUTIONDATETIME$":"Not Set",            # Execution time (set at runtime)
    "$XMLSOURCE$":"Not Set"                     # URL or pathname of XML source (set at runtime)
    }

_TSDR_dirname = os.path.dirname(__file__)

_xslt_table = {
    "ST66" : _XSLTDescriptor("ST66"),
    "ST96" : _XSLTDescriptor("ST96")
    }

class TSDRReq(object):
    '''
    TSDR request object
    '''

    def __init__(self):
        '''
        Initialize TDSR request
        '''
        self.reset()

        ### PEP 476
        if SSL_INSTALLED:
            try:
                self.UNVERIFIED_CONTEXT = ssl._create_unverified_context()
            except AttributeError:
                self.UNVERIFIED_CONTEXT = None
        else:
            self.UNVERIFIED_CONTEXT = None
        ### PEP 476

    def reset(self):
        '''
        Resets all values (but not control fields) in TDSRReq object
        '''
        # Reset control fields (XSLT transform, PTO format)
        self.unsetXSLT()
        self.unsetPTOFormat()
        # reset data fields
        self.resetXMLData() # Resetting TSDR data will cascade to CSV and TSDR map, too
        return

    def setXSLT(self, template):
        '''
        Specifies text of an XSLT transform to be used to transform the PTO-supplied
        XML data into key-value pairs.  If not set (default), one of the package-
        supplied templates will be used.
        '''
        self.XSLT = template
        return

    def unsetXSLT(self):
        '''
        Resets self.XSLT to None, causing the package-supplied templates to be used.
        '''
        self.XSLT = None
        return

    def setPTOFormat(self, PTOFormat):
        '''
        Determines what format file will be fetched from the PTO.
            "ST66": ST66-format XML
            "ST96": ST96-format XML
             "zip": zip file.  The zip file obtained from
                    the PTO is currently ST66-format XML.
        If this is unset, "zip" will be assumed.
        '''
        valid_formats = ["ST66", "ST96", "zip"]
        if PTOFormat not in valid_formats:
            raise ValueError("invalid PTO format '%s'" % PTOFormat)
        self.PTOFormat = PTOFormat
        return

    def unsetPTOFormat(self):
        '''
        Resets PTO format to "zip" (default)
        '''
        self.setPTOFormat("zip")
        return

    def resetXMLData(self):
        '''
        Resets TSDR data retrived from PTO; and CSV data (and TSDR map), which
        depends on it
        '''
        self.XMLData = None
        self.ZipData = None
        self.ImageFull = None
        self.ImageThumb = None
        self.ErrorCode = None
        self.ErrorMessage = None
        self.XMLDataIsValid = False
        self.resetCSVData()
        return

    def resetCSVData(self):
        '''
        Resets CSV data; and TSDR map, which depends on it
        '''
        self.CSVData = None
        self.CSVDataIsValid = False
        self.resetTSDRData()
        return

    def resetTSDRData(self):
        '''
        Resets TSDR mapping
        '''
        self.TSDRData = TSDRMap()
        return

    def getTSDRInfo(self, identifier=None, tmtype=None):
        '''
        Obtain XML trademark data from the PTO or local file, parse it to key/data pairs
        and produce a dictionary of TSDR information.

        Parameters:
            identifier: serial or registration number at PTO
                        filename, if fetched locally
            tmtype:
              "s" to indicate application (serial) number
              "r" to indicate registration number
              None" (or omitted): use filename

        Sets:
            self.XMLData
            self.ZipData (optional)
            self.ImageThumb (optional)
            self.ImageFull (optional)
            self.CSVData
            self.TSDRData
        '''
        self.getXMLData(identifier, tmtype)
        if self.XMLDataIsValid:
            self.getCSVData()
            if self.CSVDataIsValid:
                self.getTSDRData()
        return

    def getXMLData(self, identifier=None, tmtype=None):
        '''
        Obtain XML trademark data from the PTO or local file

        Parameters:
            identifier: serial or registration number at PTO; or
                        filename, if fetched locally
            tmtype:
              "s" to indicate application (serial) number
              "r" to indicate registration number
              None" (or omitted): use filename

        Sets:
            self.XMLData
            self.ZipData (optional)
            self.ImageThumb (optional)
            self.ImageFull (optional)
            self.CSVData
            self.TSDRData
        '''
        self.resetXMLData()        # Clear out any data from prior use
        if tmtype is None:
            self.getXMLDataFromFile(identifier)
        else:
            self.getXMLDataFromPTO(identifier, tmtype)
        return

    def getXMLDataFromFile(self, filename):
        '''
        Load TDSR data from local file (which may be a zip file or text XML file).
        This method is generally used only for testing.

        Parameters:

            filename: filename of file to be loaded

        Sets:
            self.XMLData
            self.ZipData (if file is zip file)
            self.ImageThumb (if file is zip file)
            self.ImageFull (if file is zip file)
        '''

        with open(filename, "rb") as f:
            filedata = f.read()

        _TSDR_substitutions["$XMLSOURCE$"] = filename
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        _TSDR_substitutions["$EXECUTIONDATETIME$"] = now

        self._processFileContents(filedata)
        return

    def getXMLDataFromPTO(self, number, tmtype):
        '''
        Fetch TDSR data from USPTO (either as XML file (ST66 or ST96), or as a
        zip file).

        Parameters:
            number: serial or registration number
            tmtype:
              "s" to indicate application (serial) number
              "r" to indicate registration number


        Sets:
            self.XMLData
            self.ZipData (for format="zip")
            self.ImageThumb (for format="zip")
            self.ImageFull (for format="zip")
        '''

        self._validate_PTO_parameters(number, tmtype)

        xml_url_template_st66 = "https://tsdrapi.uspto.gov/ts/cd/status66/"\
                                "%sn%s/info.xml"
        xml_url_template_st96 = "https://tsdrapi.uspto.gov/ts/cd/casestatus/"\
                                "%sn%s/info.xml"
        zip_url_template      = "https://tsdrapi.uspto.gov/ts/cd/casestatus/"\
                                "%sn%s/content.zip"
        pto_url_templates = {
            "ST66" : xml_url_template_st66,
            "ST96" : xml_url_template_st96,
            "zip"  : zip_url_template
            }

        fetchtype = self.PTOFormat
        pto_url_template = pto_url_templates[fetchtype]
        pto_url = pto_url_template % (tmtype, number)
        ##  with urllib2.urlopen(pto_url) as f:  ## This doesn't work; in Python 2.x,
        ##      filedata = f.read()              ## urlopen() does not support the "with" statement
        ## I'm only leaving this comment here because twice I've forgotten that this won't work
        ## in Python 2.7, and attempt the "with" statement before it bites me and I remember.
        try:
            ### PEP 476:
            ### use context paramenter if it is supported (TypeError if not)
            try:
                f = urllib2.urlopen(pto_url, context=self.UNVERIFIED_CONTEXT)
            except TypeError as e:
                f = urllib2.urlopen(pto_url)
        except urllib2.HTTPError as e:
            if e.code == 404:
                self.ErrorCode = "Fetch-404"
                self.ErrorMessage = "getXMLDataFromPTO: Error fetching from PTO. "\
                             "Errorcode: 404 (not found); URL: <%s>" % (pto_url)
                return
            else:
                raise

        filedata = f.read()
        f.close()

        _TSDR_substitutions["$XMLSOURCE$"] = pto_url
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        _TSDR_substitutions["$EXECUTIONDATETIME$"] = now

        self._processFileContents(filedata)
        return

    def getCSVData(self):
        '''
        Transform the XML TSDR data in self.XMLData into a list of
        name-value pairs.  If an XSLT template was supplied as an option,
        that template will be used; otherwise the method will determine the
        XML format and use the appropriate transform supplied as part of
        Plumage.

        Either getXMLDataFromPTO or getXMLDataFromFile must be
        successfully invoked before using this method.

        Parameters: none.

        Reads:
            self.XMLData
        Sets:
            self.CSVData
        '''
        self.resetCSVData()  # Clear out any data from prior use

        # First, make sure there is XML data to process
        if not self.XMLDataIsValid:
            self.CSVDataIsValid = False
            self.ErrorCode = "CSV-NoValidXML"
            self.ErrorMessage = "No valid XML data found"
            return

        # Prep the XML
        f = StringIO.StringIO(self.XMLData)
        parsed_xml = etree.parse(f)
        # if a transform template is provided, use it,
        # otherwise figure out which to use...
        if self.XSLT is not None:
            xslt_root = etree.XML(self.XSLT)
            transform = etree.XSLT(xslt_root)
            _TSDR_substitutions["$XSLTFILENAME$"] = "CALLER-PROVIDED XSLT"
            _TSDR_substitutions["$XSLTPATHNAME$"] = "CALLER-PROVIDED XSLT"
        else:
            # If XML format was specified in PTOFormat, use that; otherwise try to determine by looking
            supported_xml_formats = ["ST66", "ST96"]
            if self.PTOFormat in supported_xml_formats:
                xml_format = self.PTOFormat
            else:
                xml_format = self._determine_xml_format(parsed_xml)
                if xml_format not in supported_xml_formats:
                    self.CSVDataIsValid = False
                    self.ErrorCode = "CSV-UnsupportedXML"
                    self.ErrorMessage = "Unsupported XML format found: %s" % xml_format
                    return
            xslt_transform_info = _xslt_table[xml_format]
            transform = xslt_transform_info.transform
            _TSDR_substitutions["$XSLTFILENAME$"] = xslt_transform_info.filename
            _TSDR_substitutions["$XSLTLOCATION$"] = xslt_transform_info.location
        # Transform
        transformed_tree = transform(parsed_xml)
        csv_string = self._perform_substitution(str(transformed_tree))
        self.CSVData = self._normalize_empty_lines(csv_string)

        csvresults = self._validateCSV()
        if csvresults.CSV_OK:
            self.CSVDataIsValid = True
        else:
            self.CSVDataIsValid = False
            self.ErrorCode = csvresults.error_code
            self.ErrorMessage = csvresults.error_message
        return

    def getTSDRData(self):
        '''
        Refactor key/data pairs to dictionary.

        getCSVData must be successfully invoked before using this method.

        Parameters: none.

        Reads:
            self.CSVData
        Sets:
            self.TSDRData
        '''
        # note on general strategy:
        # generally, we read key/value pairs and simply add to dictionary
        # repeated fields will be temporarily kept in a repeated_item_dict,
        # and added at end of processing.
        #
        # When a "BeginRepeatedField" key is hit we process as follows:
        #   - allocate an empty temp dictionary for this field;
        #   - for each key/value pair encountered in the repeated field, add to the
        #     temp dictionary;
        #   - When the "EndRepeatedField" key is encountered (say, for field "FOO"):
        #       - if no "ListFOO" exists yet, create an empty list to describe the FOO
        #         field in the repeated_item dict;
        #       - add the temp dictionary to the ListFOO entry;
        #       - resume sending updates to regular dictionary, not subdict.
        # At end of processing, merge repeated-item dict into main dict.
        # First-found "Applicant" is deemed current applicant, so copy that one to
        # the main entry.

        self.resetTSDRData()     # Clear out any data from prior use

        if not self.CSVDataIsValid:
            self.ErrorCode = "Map-NoValidCSV"
            self.ErrorMessage = "No valid CSV data"
            return

        repeated_item_dict = {}
        output_dict = {}

        current_dict = output_dict
        lines = self.CSVData.split("\n")
        lines = self._drop_empty_lines(lines)
        for line in lines:
            [key, data] = line.split(',', 1)
            # normally, there will be quote marks; strip them off
            if data[0] == data[-1] == '"':
                data = data[1:-1]
            if key == "BeginRepeatedField":
                temp_dict = dict()
                current_dict = temp_dict
            elif key == "EndRepeatedField":
                # first time, allocate an empty list to be added to;
                # else re-use existing list
                if data+"List" not in repeated_item_dict:
                    repeated_item_dict[data+"List"] = []
                repeated_item_dict[data+"List"].append(current_dict)
                # done processing list, resume regular output
                current_dict = output_dict
            else:
                current_dict[key] = data
        tsdrdata = self.TSDRData
        tsdrdata.TSDRSingle = output_dict
        tsdrdata.TSDRMulti = repeated_item_dict
        tsdrdata.TSDRMapIsValid = True
        return

    def _processFileContents(self, filedata):
        # At this point, we've read data, but don't know whether its XML or zip
        stringIOfile = StringIO.StringIO(filedata)
        if zipfile.is_zipfile(stringIOfile):
            # it's a zip file, process it as a zip file, pulling XML data, and other stuff, from the zip
            self._processZip(stringIOfile, filedata)
        else:
            # it's not a zip, it's assumed XML-only; just copy to XMLData (other fields will remain None)
            self.XMLData = filedata

        error_reason = self._xml_sanity_check(self.XMLData)
        if error_reason != "":
            self.XMLDataIsValid = False
            self.ErrorCode = "XML-NoValidXML"
            self.ErrorMessage = error_reason
        else:
            self.XMLDataIsValid = True
        return

    def _xml_sanity_check(self, text):
        '''
        Quick check to see if text is valid XML; not comprehensive, just a sanity check.
        Returns string with an error reason if XML fails; or "" if XML passes
        '''

        error_reason = ""
        if (text is None) or (text == ""):
            error_reason = "getXMLData: XML data is null or empty"
        else:
            try:
                # see if this triggers an exception
                f = StringIO.StringIO(text)
                etree.parse(f)
                # no exception; passes sanity check
            except etree.XMLSyntaxError, e:
                error_reason = "getXMLData: exception(lxml.etree.XMLSyntaxError) parsing purported XML data.  "\
                                 "Reason: '<%s>'" %  e.message
        return error_reason


    def _validate_PTO_parameters(self, number, tmtype):
        '''
        Validate parameters used to fetch from PTO.

            number: string made up of 7 or 8 digits;
                7 digits for registrations, 8 for applications
            tmtype: string;
                "s" (serial number of application) or "r" (registation number).
        '''
        if tmtype not in ["s", "r"]:
            raise ValueError("Invalid tmtype value '%s' specified; " \
                             "'s' or 'r' required." % tmtype)
        if not isinstance(number, str):
            raise ValueError("Invalid identification number '%s' %s specified: " \
                             "must be string." % (number, type(number)))
        if not number.isdigit():
            raise ValueError("Invalid identification number '%s' specified: " \
                             "must be all-numeric." % number)
        if tmtype == 's':
            expected_length = 8
        else:
            expected_length = 7
        if len(number) != expected_length:
            raise ValueError("Invalid identification number '%s' specified: "\
                             "type %s should be %s digits." % \
                             (number, tmtype, expected_length))

    def _processZip(self, stringio_file, zipdata):
        '''
        process a zip file, completing appropriate fields of the TSDRReq
        '''
        # basic task, getting the xml data:
        zipf = zipfile.ZipFile(stringio_file, "r")
        xmlfiles = [name for name in zipf.namelist()
                    if name.lower().endswith(".xml")]
        assert len(xmlfiles) == 1
        xmlfilename = xmlfiles[0]
        self.XMLData = zipf.read(xmlfilename)

        # bells & whistles:
        self.ImageFull  = None
        self.ImageThumb = None
        self.ZipData    = None
        # save the images, if there are any
        try:
            self.ImageFull = zipf.read("markImage.jpg")
        except KeyError:
            pass
        try:
            self.ImageThumb = zipf.read("markThumbnailImage.jpg")
        except KeyError:
            pass
        self.ZipData = zipdata

        return

    def _determine_xml_format(self, tree):
        '''
        Given a parsed XML tree, determine its format ("ST66" or "ST96";
        or None, if not determinable)
        '''

        ST66_root_tag = \
            "{http://www.wipo.int/standards/XMLSchema/trademarks}Transaction"
        ## Former tag value for ST-96 1_D3; keeping it around as known but unsupported for diagnostic value
        ST96_1_D3_root_tag = \
            "{http://www.wipo.int/standards/XMLSchema/Trademark/1}Transaction"
        ST96_root_tag = \
            "{http://www.wipo.int/standards/XMLSchema/ST96/Trademark}TrademarkTransaction"

        tag_map = {
            ST66_root_tag : "ST66",
            ST96_1_D3_root_tag : "ST96-1_D3",
            ST96_root_tag : "ST96"
            }

        root = tree.getroot()
        tag = root.tag
        result = None   #default answer if not in the map
        if tag in tag_map:
            result = tag_map[tag]
        return result

    def _normalize_empty_lines(self, string_of_lines):
        '''
        This method takes a string of lines, separated by the system line separator
        characteor (e.g. \n), and eliminates lines that are empty or consisting entirely of
        whitespace. Its purpose is to relax what input is accepted from the the XSLT process,
        so that including empty lines is permitted and whether the final line ends with a
        newline is immaterial.
        '''
        lines = string_of_lines.split(LINE_SEPARATOR)
        lines = self._drop_empty_lines(lines)
        reassembled_string_of_lines = LINE_SEPARATOR.join(lines) + LINE_SEPARATOR
        return reassembled_string_of_lines

    def _drop_empty_lines(self, lines):
        '''
        This method takes a list of lines and drops those that are empty, where "empty"
        means either zero-length or consisting only of whitespace.
        '''
        # if anything is left after stripping away leading and trailing whitespace, keep it
        lines = [line for line in lines if len(line.strip(WHITESPACE))>0]
        return lines

    class _validateCSVResponse(object):
        '''
        Object used to hold response from _validateCSV
        Note: a simple list would be fine, but a full-fledged response object is used
        for consistency with C# and Java implementations
          CSV_OK (boolean): status of whether CSV passes sanity check; if True, error_code and error_message
                are not meaningful
          error_code (string): short error code, designed to be inspected by calling program.
          error_message (string): detailed error message, designed to be read by humans
        '''

        def __init__(self):
            '''
            initialize a _validateCSVResponse
            '''
            self.CSV_OK = True
            no_error_found_message = "getCSVData: No obvious errors parsing XML to CSV."
            self.error_code = None
            self.error_message = no_error_found_message

    def _validateCSV(self):
        '''
        validateCSV performs a naive sanity-check of the CSV for obvious errors.
        It's not bullet-proof, but catches some of the more likely problems that would
        survive the XSLT transform without errors, but potentially produce erroneous
        data that might cause hard-to-find problems downstream.

        It checks:
         * CSV data consists of more than one line (a common error is a bad XSLT
           transform that slurps in entire file as one line, especially if using an
           XSLT transform designed for ST66 on ST96 data, or vice-versa).
         * Each line must be:
              - in the format [START-OF-LINE]KEYNAME,"VALUE"[END-OF-LiNE]
              - KEYNAME consists only of letters (A-Z, a-z) and digits (0-9);
              - VALUE is enclosed in double-quotes;
              - No spaces or other whitespace anywhere except in VALUE, inside the
                quotes; not even before/after the comma or after "VALUE".

        Returns _validateCSVResponse object
        '''
        result = self._validateCSVResponse()
        comma = ","
        line_separator = "\n"
        valid_key_chars = set(string.letters + string.digits)
        try:
            lines = self.CSVData.split(line_separator)
            lines = self._drop_empty_lines(lines)
            if len(lines) < 2:
                result.error_code = "CSV-ShortCSV"
                result.error_message = "getCSVData: XML parsed to fewer than 2 lines of CSV"
                raise ValueError
            for line_number_offset in range(0, len(lines)):
                line = lines[line_number_offset]
                comma_position = line.find(',')
                if comma_position == -1:
                    result.error_code = "CSV-InvalidKeyValuePair"
                    result.error_message = "getCSVData [line %s]: " \
                        "no key-value pair found in line <%s> (missing comma)" \
                        % (line_number_offset+1, line)
                    raise ValueError
                k, v = line.split(',', 1)
                if not set(k).issubset(valid_key_chars):
                    result.error_code = "CSV-InvalidKey"
                    result.error_message = "getCSVData [line %s]: " \
                        "invalid key <%s> found (invalid characters in key)" \
                        % (line_number_offset+1, k)
                    raise ValueError
                stripped_v = v[1:-1]
                if '"' + stripped_v + '"' != v:
                    result.error_code = "CSV-InvalidValue"
                    result.error_message = "getCSVData [line %s]: " \
                        "invalid value <%s> found for key <%s> " \
                        "(does not begin and end with double-quote character)" \
                        % (line_number_offset+1, v, k)
                    raise ValueError
        except ValueError:
            if result.error_code is None:   # Not good, something we didn't count on went wrong
                result.error_code = "CSV-UnknownError"
                result.error_message = "getCSVData: unknown error validating CSV data"
            result.CSV_OK = False
        return result

    def _perform_substitution(self, s):
        '''
        Substitute run-time data for $placeholders from XSLT
        '''
        for variable in _TSDR_substitutions:
            s = s.replace(variable, _TSDR_substitutions[variable])
        return s

class TestSelf(unittest.TestCase):
    '''
    Simple self-test
    '''

    def setUp(self):
        pass

    def test_00_selftest(self):
        '''
        Simple self-test
        '''
        t = TSDRReq()
        t.getTSDRInfo("sn76044902.zip")
        self.assertTrue(t.XMLDataIsValid)
        self.assertEqual(len(t.XMLData), 30354)
        self.assertEqual(t.XMLData[0:55], r'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
        self.assertEqual(t.ImageThumb[6:10], "JFIF")
        self.assertEqual(t.ImageFull[0:4], "\x89PNG")
        self.assertTrue(t.CSVDataIsValid)
        self.assertEqual(len(t.CSVData.split("\n")), 290)
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

if __name__ == "__main__":
    # self-test if run as command
    unittest.main()