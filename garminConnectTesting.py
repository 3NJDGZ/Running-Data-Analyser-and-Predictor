import garminconnect as garmin 

tokenstore = "~/.garminconnect"
garminClient = garmin.Garmin()

garminClient.login(tokenstore)
print(f"Full name: {garminClient.get_full_name()}")
