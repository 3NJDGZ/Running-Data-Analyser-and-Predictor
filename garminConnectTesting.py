import garminconnect as garmin 
from garminconnect import GarminConnectAuthenticationError, GarminConnectConnectionError, GarminConnectTooManyRequestsError
from garth.exc import GarthHTTPError
import os 

tokenstore = os.getenv("GARMINTOKENS") or "~/.garminconnect"
try:
    email = input("Enter Email: ")
    pwd = input("Enter password: ")
    garminClient = garmin.Garmin(email=email, password=pwd)

    garminClient.login()
    garminClient.garth.dump(tokenstore)
    print(f"Full name: {garminClient.get_full_name()}")

    # gets all the activities, and filters them by if they are a running activity
    activities = garminClient.get_activities(0, 10)

    if activities is not None:
        for activity in activities:
            if activity['activityType']['typeId'] == 1:
                print(f"Activity: {activity}\n")

except (GarminConnectAuthenticationError, 
        GarminConnectConnectionError, 
        GarminConnectTooManyRequestsError, 
        GarthHTTPError) as e:
    print(f"Error encountered!\n---- Error Message ----\n{e}")
