'''
Plumage:
    Python module to obtain trademark status information from USPTO's TSDR system

To use:
    from Plumage import plumage
    t = plumage.TSDRReq()
    t.getTSDRInfo("75181334", "s") 

For details, see https://github.com/codingatty/Plumage/wiki
'''

# Version 1.4.0, 2020-10-03
# Copyright 2014-2020 Terry Carroll
# carroll@tjc.com
#
# License information:
#
# This program is licensed under Apache License, version 2.0 (January 2004);
# see http://www.apache.org/licenses/LICENSE-2.0
# SPX-License-Identifier: Apache-2.0
#
# Anyone who makes use of, or who modifies, this code is encouraged
# (but not required) to notify the author.

import io
import urllib.request
import urllib.error

import sys

import zipfile
import os.path
import string
import time
from datetime  import datetime
from datetime  import timedelta
import unittest
from lxml import etree
import json

### PEP 476 begin
try:
    import ssl
    SSL_INSTALLED = True
except ImportError:
    SSL_INSTALLED = False
### PEP 476 end

__version__ = "1.4.0-pre"
__last_updated__ = "2020-10-03"
__author__ = "Terry Carroll"
__URL__ = "https://github.com/codingatty/Plumage-py"
__copyright__ = "Copyright 2014-2020 Terry Carroll"
__license__ = "Apache License, version 2.0 (January 2004)"
__SPDX_LID__ = "Apache-2.0"
__licenseURL__ = "http://www.apache.org/licenses/LICENSE-2.0"

COMMA = ","
LINE_SEPARATOR = "\n"
WHITESPACE = string.whitespace

_TSDR_dirname = os.path.dirname(__file__)

def GetMetainfo():
    return metainfo

def SetIntervalTime(value):
    try:
        TSDRReq._TSDR_minimum_interval = 0 + value # force an error if non-numeric
    except TypeError:
        raise TypeError("interval value must be an int or float")

def ResetIntervalTime():
    TSDRReq._TSDR_minimum_interval = TSDRReq._default_TSDR_minimum_interval

def GetIntervalTime():
    return TSDRReq._TSDR_minimum_interval

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
        with open(xslt_pathname, "rb") as _f:
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


class TSDRReq(object):
    '''
    TSDR request object
    '''

    _prior_TSDR_call_time = None   # time of previous TSDR call (real or simulated), if any
    _default_TSDR_minimum_interval = 1.0 # at least one second between calls to TSDR (real or simulated)
    _TSDR_minimum_interval = _default_TSDR_minimum_interval     

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
        # reset control fields (XSLT transform, PTO format)
        self.resetXSLT()
        self.resetPTOFormat()
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

    def resetXSLT(self):
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
        If this is reset, "zip" will be assumed.
        '''
        valid_formats = ["ST66", "ST96", "zip"]
        if PTOFormat not in valid_formats:
            raise ValueError("invalid PTO format '%s'" % PTOFormat)
        self.PTOFormat = PTOFormat
        return

    def resetPTOFormat(self):
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
        
        if TSDRReq._prior_TSDR_call_time is not None:
            _waitFromTime(TSDRReq._prior_TSDR_call_time, TSDRReq._TSDR_minimum_interval)
        TSDRReq._prior_TSDR_call_time = datetime.now()

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
        _TSDR_substitutions["$XMLSOURCE$"] = filename

        # save date/time (both pseudo-TSDR call as ISO-8601 and simple YYY-MM-DD HH:MM:SS)
        now = datetime.now()
        _TSDR_substitutions["$TSDRSTARTDATETIME$"] = now.isoformat(timespec='microseconds')
        _TSDR_substitutions["$EXECUTIONDATETIME$"] = now.strftime("%Y-%m-%d %H:%M:%S")

        with open(filename, "rb") as f:
            filedata = f.read()

        # save pseudo-TSDR completion date/time ISO-8601 
        now = datetime.now()
        #now = time.strftime("%Y-%m-%d %H:%M:%S")
        _TSDR_substitutions["$TSDRCOMPLETEDATETIME$"] = now.isoformat(timespec='microseconds')

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

        _TSDR_substitutions["$XMLSOURCE$"] = pto_url
        # save date/time (both TSDR call as ISO-8601 and simple YYY-MM-DD HH:MM:SS)
        now = datetime.now()
        _TSDR_substitutions["$TSDRSTARTDATETIME$"] = now.isoformat(timespec='microseconds')
        _TSDR_substitutions["$EXECUTIONDATETIME$"] = now.strftime("%Y-%m-%d %H:%M:%S")

        ##  with urllib2.urlopen(pto_url) as f:  ## This doesn't work; in Python 2.x,
        ##      filedata = f.read()              ## urlopen() does not support the "with" statement
        ## I'm only leaving this comment here because twice I've forgotten that this won't work
        ## in Python 2.7, and attempt the "with" statement before it bites me and I remember.
        try:
            ### PEP 476:
            ### use context parameter if it is supported (TypeError if not)
            try:
                f = urllib.request.urlopen(pto_url, context=self.UNVERIFIED_CONTEXT)
            except TypeError as e:
                f = urllib.request.urlopen(pto_url)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                self.ErrorCode = "Fetch-404"
                self.ErrorMessage = "getXMLDataFromPTO: Error fetching from PTO. "\
                             "Errorcode: 404 (not found); URL: <%s>" % (pto_url)
                return
            else:
                raise

        filedata = f.read()
        f.close()

        # save TSDR completion date/time ISO-8601 
        now = datetime.now()
        #now = time.strftime("%Y-%m-%d %H:%M:%S")
        _TSDR_substitutions["$TSDRCOMPLETEDATETIME$"] = now.isoformat(timespec='microseconds')

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
        f = io.BytesIO(self.XMLData.encode(encoding="utf-8"))
        parsed_xml = etree.parse(f)
        # if a transform template is provided, use it,
        # otherwise figure out which to use...
        if self.XSLT is not None:
            # Py3 req's byte-string or string w/o Unicode declaration
            override_XSLT = self.XSLT.encode(encoding="utf-8")
            xslt_root = etree.XML(override_XSLT)
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
            [key, data] = line.split(COMMA, 1)
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
        # At this point, we've read data (as binary), but don't know whether its XML or zip
        in_memory_file = io.BytesIO(filedata)
        if zipfile.is_zipfile(in_memory_file):
            # it's a zip file, process it as a zip file, pulling XML data, and other stuff, from the zip
            self._processZip(in_memory_file, filedata)
        else:
            # it's not a zip, it's assumed XML-only;
            # store to XMLData (other fields will remain None)
            #Python 3, filedata is bytes; must encode to a (Unicode) string
            self.XMLData = filedata.decode(encoding="utf-8")

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
                f = io.BytesIO(text.encode(encoding="utf-8"))
                etree.parse(f)
                # no exception; passes sanity check
            except etree.XMLSyntaxError as e:
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

    def _processZip(self, in_memory_file, zipdata):
        '''
        process a zip file, completing appropriate fields of the TSDRReq
        '''
        # basic task, getting the xml data:
        zipf = zipfile.ZipFile(in_memory_file, "r")
        xmlfiles = [name for name in zipf.namelist()
                    if name.lower().endswith(".xml")]
        assert len(xmlfiles) == 1
        xmlfilename = xmlfiles[0]
        xml_data_from_zipfile = zipf.read(xmlfilename)
        # In Python 3, ZipFile.read() returns bytes; must encode into a string
        self.XMLData = xml_data_from_zipfile.decode(encoding="utf-8")
        
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
        valid_key_chars = set(string.ascii_letters + string.digits)
        try:
            lines = self.CSVData.split(LINE_SEPARATOR)
            lines = self._drop_empty_lines(lines)
            if len(lines) < 2:
                result.error_code = "CSV-ShortCSV"
                result.error_message = "getCSVData: XML parsed to fewer than 2 lines of CSV"
                raise ValueError
            for line_number_offset in range(0, len(lines)):
                line = lines[line_number_offset]
                comma_position = line.find(COMMA)
                if comma_position == -1:
                    result.error_code = "CSV-InvalidKeyValuePair"
                    result.error_message = "getCSVData [line %s]: " \
                        "no key-value pair found in line <%s> (missing comma)" \
                        % (line_number_offset+1, line)
                    raise ValueError
                k, v = line.split(COMMA, 1)
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

def _waitFromTime(fromtime, duration):
    '''
    Wait until the specified duration (in seconds) after fromtime (datetime) has occurred
    '''
    DEBUG = False
    now = datetime.now()
    if DEBUG: print(datetime.now(), "ENTERING _waitFromTime")
    td = timedelta(seconds=duration)
    end_time = fromtime+td
    pause_time = (end_time - now).total_seconds()
    if DEBUG:  print("required pause time (seconds):", pause_time)
    if pause_time > 0:
        if DEBUG: print(datetime.now(), "Still need to pause")
        time.sleep(pause_time)
    if DEBUG: print(datetime.now(), "EXITING _waitFromTime")


lib_metainfo = {                               # metainfo specific to this library (i.e., not copied XSLT)
    "MetaInfoLibraryName": "Plumage-py",
    "MetaInfoLibraryVersion": __version__,
    "MetaInfoLibraryDate": __last_updated__,
    "MetaInfoLibraryAuthor": __author__,
    "MetaInfoLibraryURL": __URL__,
    "MetaInfoLibraryCopyright": __copyright__,
    "MetaInfoLibraryLicense": __license__,
    "MetaInfoLibrarySPDXLicenseIdentifier": __SPDX_LID__,
    "MetaInfoLibraryLicenseURL": __licenseURL__
}

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
    "$EXECUTIONDATETIME$":"Not Set",            # Execution timestamp, YYYY-MM-DD HH:MM:SS format (set at runtime)
    "$TSDRSTARTDATETIME$":"Not Set",            # TSDR call start timestamp, ISO-8601 format (set at runtime)
    "$TSDRCOMPLETEDATETIME$":"Not Set",         # TSDR call start timestamp, ISO-8601 format (set at runtime)
    "$XMLSOURCE$":"Not Set"                     # URL or pathname of XML source (set at runtime)
    }

_xslt_table = {
    "ST66" : _XSLTDescriptor("ST66"),
    "ST96" : _XSLTDescriptor("ST96")
    }

metainfo = {}         # will hold metainfo (plumage library metainfo and plumage XSLT metainfo from JSON file)

XSLT_metainfo_filename = "Plumage-XSLT-metadata.json"
XSLT_metainfo_path = os.path.join(_TSDR_dirname, XSLT_metainfo_filename)
with open(XSLT_metainfo_path, 'r') as JSON_file:
        XSLT_metainfo = json.load(JSON_file)
metainfo.update(lib_metainfo)
metainfo.update(XSLT_metainfo)

if __name__ == "__main__":
    # if run as command, print short documentation and exit
    print(__doc__)