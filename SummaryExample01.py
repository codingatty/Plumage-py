from Plumage import plumage
t = plumage.TSDRReq()
t.getTSDRInfo("2564831", "r")   # get info on reg. no 2,564,831
tsdrdata=t.TSDRData
if tsdrdata.TSDRMapIsValid:
   print "Application serial no: ", tsdrdata.TSDRSingle["ApplicationNumber"]
   print "Trademark text: ", tsdrdata.TSDRSingle["MarkVerbalElementText"]
   print "Application filing date: ", tsdrdata.TSDRSingle["ApplicationDate"]
   print "Registration no: ", tsdrdata.TSDRSingle["RegistrationNumber"]
   # Owner info is in most recent (0th) entry in ApplicantList
   applicant_list = tsdrdata.TSDRMulti["ApplicantList"]
   current_owner_info = applicant_list[0]
   print "Owner:", current_owner_info["ApplicantName"]
   print "Owner address: ", current_owner_info["ApplicantCombinedAddress"]
   # Get most recent event: 0th entry in event list
   event_list = tsdrdata.TSDRMulti["MarkEventList"]
   most_recent_event = event_list[0]
   print "Most recent event: ", most_recent_event["MarkEventDescription"]
   print "Event date: ", most_recent_event["MarkEventDate"]