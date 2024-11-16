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
        activity_ids = []  # get the unique ids of each activity so we can get the 'detailed' activities object via the 'get_activity()' function
        for activity in activities:
            rst = activity.sport_type # relaxed sport type
            if rst.root == "Run" and len(activity_ids) <= 4:
                print(activity.id)
                activity_ids.append(activity.id)
        return activity_ids

    
    def getActivityData(self, client: Client):
        strava_athlete = client.get_athlete()
        activity_data = []  # will be used to hold data
        activity_ids = self.getRunningActivitiesID(client)
        # check if data entry already exists in mongoDB, if not then insert into database
        for activityID in activity_ids:
            if self.__cacheClient.getDataFromKey(self.__cacheClient.createKey(activityID)) is None and self.__dbClient.retrieveRunningData(activityID, strava_athlete.id) is None:
                print("Data not found in both redis DB and MongoDB!")
                activityName = client.get_activity(activityID).name
                averageHeartRate = client.get_activity(activityID).average_heartrate
                distance = client.get_activity(activityID).distance
                elapsedTime = client.get_activity(activityID).elapsed_time
                elevationHigh = client.get_activity(activityID).elev_high
                elevationLow = client.get_activity(activityID).elev_low
                elevationGain = elevationHigh - elevationLow
                elevationGain = round(elevationGain, 1)

                activity_streams = client.get_activity_streams(
                    activityID, types=["heartrate"], resolution="low"
                )

                # getting HR stream data
                if "heartrate" in activity_streams.keys():
                    hrStream = activity_streams["heartrate"].data
                else:
                    hrStream = [0]

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
                        "activity_name": activityName
                    }

                activity_data.append(dataToBeAdded)

                self.__dbClient.insertRunningData(strava_athlete.id, client.get_activity(activityID).id, distance, elapsedTime, elevationHigh, elevationLow, predictedIntensity, averageHeartRate, activityName, strava_athlete.firstname, hrStream)
                
                # insert data into Redis
                self.__cacheClient.insertJSONData(600, self.__cacheClient.createKey(activityID), dataToBeAdded)
            else:
                # get data from redis cloud cache instead of mongoDB
                dataToBeAdded = self.__cacheClient.getDataFromKey(self.__cacheClient.createKey(activityID))

                if dataToBeAdded is not None:
                    # data formatting  
                    activity_data.append(
                        {
                            "average_heart_rate": dataToBeAdded["average_heart_rate"],
                            "distance": dataToBeAdded["distance"],
                            "elapsed_time": dataToBeAdded["elapsed_time"],
                            "elevation_gain": dataToBeAdded["elevation_gain"],
                            "predicted_intensity": dataToBeAdded["predicted_intensity"],
                            "activity_name": dataToBeAdded["activity_name"]
                        }
                    )
                    print("Data Entry already exists on redis DB!")
                    print("Getting data from redis DB!")
                else:
                    print("Data does not exist on redis DB! ")
                    print("Getting data from mongoDB!")
                    dataToBeAdded = self.__dbClient.retrieveRunningData(activityID, strava_athlete.id)

                    test = {
                        "average_heart_rate": dataToBeAdded["AVGHR"],
                        "distance": dataToBeAdded["Distance"],
                        "elapsed_time": dataToBeAdded["ElapsedTime"],
                        "elevation_gain": round((dataToBeAdded["ElevationH"] - dataToBeAdded["ElevationL"]), 1),
                        "predicted_intensity": dataToBeAdded["PredictedIntensity"],
                        "activity_name": dataToBeAdded["ActivityName"]
                        }

                    activity_data.append(
                        {
                            "average_heart_rate": dataToBeAdded["AVGHR"],
                            "distance": dataToBeAdded["Distance"],
                            "elapsed_time": dataToBeAdded["ElapsedTime"],
                            "elevation_gain": round((dataToBeAdded["ElevationH"] - dataToBeAdded["ElevationL"]), 1),
                            "predicted_intensity": dataToBeAdded["PredictedIntensity"],
                            "activity_name": dataToBeAdded["ActivityName"]
                        }
                    )
                    print(test)

                    # insert into redis database
                    self.__cacheClient.insertJSONData(600, self.__cacheClient.createKey(activityID), test)
                    print("Inserting data into redis DB!")

        return activity_data
        
