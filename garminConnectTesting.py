import garminconnect as garmin 
import os 

tokenstore = os.getenv("GARMINTOKENS") or "~/.garminconnect"
email = input("Enter Email: ")
pwd = input("Enter password: ")
garminClient = garmin.Garmin(email=email, password=pwd)

garminClient.login()
garminClient.garth.dump(tokenstore)
print(f"Full name: {garminClient.get_full_name()}")
