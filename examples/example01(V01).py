from Plumage import plumage
# This example works through Plumage-py v1.1
t = plumage.TSDRReq()
t.getTSDRInfo("75181334", "s")   # get info on application ser. no 75/181,334
if t.TSDRMapIsValid:
   print "Application serial no: ", t.TSDRMap["ApplicationNumber"]
   print "Trademark text: ", t.TSDRMap["MarkVerbalElementText"]
   print "Application filing date: ", t.TSDRMap["ApplicationDate"]
   print "Registration no: ", t.TSDRMap["RegistrationNumber"]
   # Owner info is in most recent (0th) entry in ApplicantList
   applicant_list = t.TSDRMap["ApplicantList"]
   current_owner_info = applicant_list[0]
   print "Owner:", current_owner_info["ApplicantName"]
   print "Owner address: ", current_owner_info["ApplicantCombinedAddress"]
   # Get most recent event: 0th entry in event list
   event_list = t.TSDRMap["MarkEventList"]
   most_recent_event = event_list[0]
   print "Most recent event: ", most_recent_event["MarkEventDescription"]
   print "Event date: ", most_recent_event["MarkEventDate"]