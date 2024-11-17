from kMeansClustering import kmeans_predictor
from website.cachingService.cachingClient import CacheClient
from website.cachingService.databaseClient import DatabaseClient
from stravalib import Client

class CachingSystem:
    def __init__(self, cacheClient: CacheClient, dbClient: DatabaseClient):
        self.__cacheClient = cacheClient
        self.__dbClient = dbClient

    def getRunningActivitiesID(self, client: Client):
        activities = client.get_activities(None, None, 15) 
        activityIDs = []  # get the unique ids of each activity so we can get the 'detailed' activities object via the 'get_activity()' function
        for activity in activities:
            rst = activity.sport_type # relaxed sport type
            if rst.root == "Run" and len(activityIDs) <= 4:
                print(activity.id)
                activityIDs.append(activity.id)
        return activityIDs
    
    def getActivityData(self, client: Client):
        stravaAthlete = client.get_athlete()
        activityDataToDisplay = []  # will be used to hold data
        activityIDs = self.getRunningActivitiesID(client)
        # check if data entry already exists in mongoDB, if not then insert into database
        for activityID in activityIDs:
            if self.__cacheClient.getDataFromKey(self.__cacheClient.createKey(activityID)) is None and self.__dbClient.retrieveRunningData(activityID, stravaAthlete.id) is None:
                print("Data not found in both redis DB and MongoDB!")
                activityName = client.get_activity(activityID).name
                averageHeartRate = client.get_activity(activityID).average_heartrate
                distance = client.get_activity(activityID).distance
                elapsedTime = client.get_activity(activityID).elapsed_time
                elevationHigh = client.get_activity(activityID).elev_high
                elevationLow = client.get_activity(activityID).elev_low
                elevationGain = elevationHigh - elevationLow
                elevationGain = round(elevationGain, 1)

                activityStreams = client.get_activity_streams(
                    activityID, types=["heartrate"], resolution="low"
                )

                # getting HR stream data
                if "heartrate" in activityStreams.keys():
                    HRStream = activityStreams["heartrate"].data
                else:
                    HRStream = [0]

                # predict intensity of the run
                predictedIntensity = kmeans_predictor.predict(
                    distance, elevationGain, elapsedTime, averageHeartRate
                )

                # setup the data to show on webpage
                dataToBeAdded = {
                        "average_heart_rate": averageHeartRate,
                        "distance": distance,
                        "elapsed_time": elapsedTime,
                        "elevation_gain": elevationGain,
                        "predicted_intensity": predictedIntensity,
                        "activity_name": activityName,
                        "HRStream": HRStream
                    }

                activityDataToDisplay.append(dataToBeAdded)

                # insert data into mongoDB
                self.__dbClient.insertRunningData(stravaAthlete.id, client.get_activity(activityID).id, distance, elapsedTime, elevationHigh, elevationLow, predictedIntensity, averageHeartRate, activityName, stravaAthlete.firstname, HRStream)
                
                # insert data into Redis
                self.__cacheClient.insertJSONData(600, self.__cacheClient.createKey(activityID), dataToBeAdded)
            else:
                # get data from redis cloud cache instead of mongoDB
                dataToBeAdded = self.__cacheClient.getDataFromKey(self.__cacheClient.createKey(activityID))

                if dataToBeAdded is not None:
                    # data formatting  
                    activityDataToDisplay.append(
                        {
                            "average_heart_rate": dataToBeAdded["average_heart_rate"],
                            "distance": dataToBeAdded["distance"],
                            "elapsed_time": dataToBeAdded["elapsed_time"],
                            "elevation_gain": dataToBeAdded["elevation_gain"],
                            "predicted_intensity": dataToBeAdded["predicted_intensity"],
                            "activity_name": dataToBeAdded["activity_name"],
                            "HRStream": dataToBeAdded["HRStream"]
                        }
                    )
                    print("Data Entry already exists on redis DB!")
                    print("Getting data from redis DB!")
                else:
                    print("Data does not exist on redis DB! ")
                    print("Getting data from mongoDB!")
                    dataToBeAdded = self.__dbClient.retrieveRunningData(activityID, stravaAthlete.id)

                    jsonRedisData = {
                        "average_heart_rate": dataToBeAdded["AVGHR"],
                        "distance": dataToBeAdded["Distance"],
                        "elapsed_time": dataToBeAdded["ElapsedTime"],
                        "elevation_gain": round((dataToBeAdded["ElevationH"] - dataToBeAdded["ElevationL"]), 1),
                        "predicted_intensity": dataToBeAdded["PredictedIntensity"],
                        "activity_name": dataToBeAdded["ActivityName"],
                        "HRStream": dataToBeAdded["HRStream"]
                        }

                    activityDataToDisplay.append(
                        {
                            "average_heart_rate": dataToBeAdded["AVGHR"],
                            "distance": dataToBeAdded["Distance"],
                            "elapsed_time": dataToBeAdded["ElapsedTime"],
                            "elevation_gain": round((dataToBeAdded["ElevationH"] - dataToBeAdded["ElevationL"]), 1),
                            "predicted_intensity": dataToBeAdded["PredictedIntensity"],
                            "activity_name": dataToBeAdded["ActivityName"]
                        }
                    )

                    # insert into redis database
                    self.__cacheClient.insertJSONData(600, self.__cacheClient.createKey(activityID), jsonRedisData)
                    print("Inserting data into redis DB!")

        return activityDataToDisplay
        
