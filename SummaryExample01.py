from Plumage import plumage
t = plumage.TSDRReq()
t.getTSDRInfo("2564831", "r")   # get info on reg. no 2,564,831
if t.TSDRMapIsValid:
   print "Application serial no: ", t.TSDRMap["ApplicationNumber"]
   print "Trademark text: ", t.TSDRMap["MarkVerbalElementText"]
   print "Application filing date: ", t.TSDRMap["ApplicationDate"]
   print "Registration no: ", t.TSDRMap["RegistrationNumber"]
   # Owner info is in most recent (0th) entry in ApplicantList
   applicant_list = t.TSDRMapLists["ApplicantList"]
   current_owner_info = applicant_list[0]
   print "Owner:", current_owner_info["ApplicantName"]
   print "Owner address: ", current_owner_info["ApplicantCombinedAddress"]
   # Get most recent event: 0th entry in event list
   event_list = t.TSDRMapLists["MarkEventList"]
   most_recent_event = event_list[0]
   print "Most recent event: ", most_recent_event["MarkEventDescription"]
   print "Event date: ", most_recent_event["MarkEventDate"]