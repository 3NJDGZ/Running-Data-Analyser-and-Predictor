from kMeansClustering import kmeans_predictor
from datetime import datetime
from website.cachingService.cachingClient import CacheClient
from website.cachingService.databaseClient import DatabaseClient
from garminconnect import Garmin

class CachingSystem:
    def __init__(self, cacheClient: CacheClient, dbClient: DatabaseClient):
        self.__cacheClient = cacheClient
        self.__dbClient = dbClient

    def getRunningActivitiesID(self, garminClient: Garmin):
        activityIDs = []  
        activities = garminClient.get_activities()

        if activities is not None:
            for activity in activities:
                if activity['activityType']['typeId'] == 1:
                    activityIDs.append(activity["activityId"])
        return activityIDs
    
    def getActivityData(self, garminClient: Garmin):
        activityDataToDisplay = []  # will be used to hold data
        activityIDs = self.getRunningActivitiesID(garminClient)

        for activityID in activityIDs:
            activity = garminClient.get_activity(activity_id=activityID)
            if activity is not None:
                if self.__cacheClient.getDataFromKey(self.__cacheClient.createKey(activityID)) is None and self.__dbClient.retrieveRunningData(activityID) is None:
                    print("Data not in RedisDB Cache and MongoDB!")
                    athleteName = garminClient.get_full_name()
                    activityName = activity["activityName"]
                    averageHR = activity["summaryDTO"]["averageHR"]
                    distanceRan = activity["summaryDTO"]["distance"]
                    elapsedTime = activity["summaryDTO"]["duration"]
                    elevationGain = activity["summaryDTO"]["elevationGain"]
                    athleteID = activity["userProfileId"]

                    # getting the date the run was ran, and formatting in YYYY-MM-DD
                    dateRan = activity["summaryDTO"]["startTimeLocal"]
                    parsedDateTime = datetime.strptime(dateRan, "%Y-%m-%dT%H:%M:%S.%f")
                    formattedDate = parsedDateTime.strftime("%Y-%m-%d")

                    # formatting HR stream data correctly
                    hrStreamData = garminClient.get_heart_rates(formattedDate)['heartRateValues']
                    HRStream = [hr for _, hr in hrStreamData if hr is not None]

                    # predict intensity of run
                    predictedIntensity = kmeans_predictor.predict(distanceRan, elevationGain, elapsedTime, averageHR)
                    dataToBeAdded = {
                        "athleteID": athleteID,
                        "athleteName": athleteName,
                        "activityID": activityID,
                        "activityName": activityName,
                        "distanceRan": distanceRan,
                        "elapsedTime": elapsedTime,
                        "predictedIntensity": predictedIntensity,
                        "averageHR": averageHR,
                        "elevationGain": elevationGain,
                        "HRStream": HRStream
                    }

                    activityDataToDisplay.append(dataToBeAdded)

                    # insert into mongoDB 
                    print("Inserting into MongoDB!")
                    self.__dbClient.insertRunningData(athleteID, activityID, distanceRan, elapsedTime, elevationGain, predictedIntensity, averageHR, activityName, athleteName, HRStream)

                    # insert data into Redis
                    print("Inserting into RedisDB Cache!")
                    self.__cacheClient.insertJSONData(600, self.__cacheClient.createKey(activityID), dataToBeAdded)
                else:
                    # check redisDB cache
                    dataToBeAdded = self.__cacheClient.getDataFromKey(self.__cacheClient.createKey(activityID))

                    if dataToBeAdded is not None:
                        activityDataToDisplay.append({
                            "athleteID": dataToBeAdded["athleteID"],
                            "athleteName": dataToBeAdded["athleteName"],
                            "activityID": dataToBeAdded["activityID"],
                            "activityName": dataToBeAdded["activityName"],
                            "distanceRan": dataToBeAdded["distanceRan"],
                            "elapsedTime": dataToBeAdded["elapsedTime"],
                            "predictedIntensity": dataToBeAdded["predictedIntensity"],
                            "averageHR": dataToBeAdded["averageHR"],
                            "HRStream": dataToBeAdded["HRStream"] 
                        })

                        print("Data already exists on redis!")
                        print("Retrieving from redis!")
                    else:
                        print("Data does not exist on redis!")
                        print("Retrieving data from mongoDB!")

                        dataToBeAdded = self.__dbClient.retrieveRunningData(activityID)

                        if dataToBeAdded is not None:
                            jsonRedisData = {
                                "athleteID": dataToBeAdded["athleteID"],
                                "athleteName": dataToBeAdded["athleteName"],
                                "activityID": dataToBeAdded["activityID"],
                                "activityName": dataToBeAdded["activityName"],
                                "distanceRan": dataToBeAdded["distanceRan"],
                                "elapsedTime": dataToBeAdded["elapsedTime"],
                                "predictedIntensity": dataToBeAdded["predictedIntensity"],
                                "averageHR": dataToBeAdded["averageHR"],
                                "HRStream": dataToBeAdded["HRStream"]
                                }

                            activityDataToDisplay.append(jsonRedisData)
                            # insert into redis database
                            self.__cacheClient.insertJSONData(600, self.__cacheClient.createKey(activityID), jsonRedisData)
                            print("Inserting data into redis DB!")


        return activityDataToDisplay
