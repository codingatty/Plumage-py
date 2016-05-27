'''
Obtain information on a federal trademark registration or application
for registration from the US Patent and Trademark Office's Trademark
Status and Document Retrieval (TSDR) system at http://tsdr.uspto.gov.

PREREQUISITES
lxml XML toolkit, http://lxml.de/

EXAMPLE

>>> from Plumage import plumage
>>> t = plumage.TSDRReq()
>>> # Python trademark application, ser. no. 76/044,902
>>> t.getTSDRInfo("s", "76044902")
>>> # Show application number and date, registration number and date...
>>> t.tmdict["ApplicationNumber"]
'76044902'
>>> t.tmdict["ApplicationDate"]
'2000-05-09-04:00'
>>> t.tmdict["RegistrationNumber"]
'2824281'
>>> t.tmdict["RegistrationDate"]
'2004-03-23-05:00'
>>> # Show trademark text and owner...
>>> t.tmdict["MarkVerbalElementText"]
'PYTHON'
>>> # Show current status of mark, and date of that status...
>>> t.tmdict["MarkCurrentStatusExternalDescriptionText"]
'A Sections 8 and 15 combined declaration has been accepted and acknowledged.'
>>> t.tmdict["MarkCurrentStatusDate"]
'2010-09-08-04:00'
>>> applicant_info = t.TSDRMap["ApplicantList"][0]
>>> applicant_info["ApplicantName"]
'PYTHON SOFTWARE FOUNDATION'
>>>
'''
