import garminconnect as garmin
import os

class GarminUserClient:
    def __init__(self):
        self.__garminClient = None
        self.__tokenstore = os.getenv("GARMINTOKENS") or "~/.garminconnect"

    def loginAndCreateClient(self, email, password):
        self.__garminClient = garmin.Garmin(email, password)
        self.__garminClient.login()
        self.__garminClient.garth.dump(self.__tokenstore)

    def getGarminClient(self):
        if self.__garminClient is not None:
            return self.__garminClient

