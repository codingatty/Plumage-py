from Plumage import plumage
t = plumage.TSDRReq()
t.getTSDRInfo("2564831", "r")   # get info on reg. no 2,564,831
if t.TSDRMapIsValid:
   print "Application serial no: ", t.TSDRMap["ApplicationNumber"]
   print "Trademark text: ", t.TSDRMap["MarkVerbalElementText"]
   print "Application filing date: ", t.TSDRMap["ApplicationDate"]
   print "Registration no: ", t.TSDRMap["RegistrationNumber"]
   print "Status: ", t.TSDRMap["MarkCurrentStatusExternalDescriptionText"]
   # Owner info is in most recent (0th) entry in ApplicantList
   current_owner_info = t.TSDRMap["ApplicantList"][0]
   print "Owner:", current_owner_info["ApplicantName"]
   print "Owner address: ", current_owner_info["ApplicantCombinedAddress"]