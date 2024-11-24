from kMeansClustering import kmeans_predictor
from datetime import datetime
import json
from website.cachingService.cachingClient import CacheClient
from website.cachingService.databaseClient import DatabaseClient
from garminconnect import Garmin

class CachingSystem:
    def __init__(self, cacheClient: CacheClient, dbClient: DatabaseClient):
        self.__cacheClient = cacheClient
        self.__dbClient = dbClient

    def getRunningActivitiesID(self, garminClient: Garmin):
        activityIDs = []  # get the unique ids of each activity so we can get the 'detailed' activities object via the 'get_activity()' function
        activities = garminClient.get_activities(0, 15)

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
                activityName = activity["activityName"]
                averageHeartRate = activity["summaryDTO"]["averageHR"]
                distanceRan = activity["summaryDTO"]["distance"]
                elapsedTime = activity["summaryDTO"]["duration"]
                elevationGain = activity["summaryDTO"]["elevationGain"]

                # getting the date the run was ran, and formatting in YYYY-MM-DD
                dateRan = activity["summaryDTO"]["startTimeLocal"]
                parsedDateTime = datetime.strptime(dateRan, "%Y-%m-%dT%H:%M:%S.%f")
                formattedDate = parsedDateTime.strftime("%Y-%m-%d")

                # formatting HR stream data correctly
                hrStreamData = garminClient.get_heart_rates(formattedDate)['heartRateValues']
                HRStream = [hr for _, hr in hrStreamData if hr is not None]

                # predict intensity of run
                predictedIntensity = kmeans_predictor.predict(distanceRan, elevationGain, elapsedTime, averageHeartRate)
                dataToBeAdded = {
                            "averageHeartRate": averageHeartRate,
                            "distanceRan": distanceRan,
                            "elapsedTime": elapsedTime,
                            "elevationGain": elevationGain,
                            "predictedIntensity": predictedIntensity,
                            "activityName": activityName,
                            "HRStream": HRStream
                        }
                activityDataToDisplay.append(dataToBeAdded)


        return activityDataToDisplay
        # # check if data entry already exists in mongoDB, if not then insert into database
        # for activityID in activityIDs:
        #     if self.__cacheClient.getDataFromKey(self.__cacheClient.createKey(activityID)) is None and self.__dbClient.retrieveRunningData(activityID, stravaAthlete.id) is None:
        #         print("Data not found in both redis DB and MongoDB!")
        #         activityName = garminClient.get_activity(activityID).name
        #         averageHeartRate = garminClient.get_activity(activityID).average_heartrate
        #         distance = garminClient.get_activity(activityID).distance
        #         elapsedTime = garminClient.get_activity(activityID).elapsed_time
        #         elevationHigh = garminClient.get_activity(activityID).elev_high
        #         elevationLow = garminClient.get_activity(activityID).elev_low
        #         elevationGain = elevationHigh - elevationLow
        #         elevationGain = round(elevationGain, 1)
        #
        #         activityStreams = garminClient.get_activity_streams(
        #             activityID, types=["heartrate"], resolution="low"
        #         )
        #
        #         # getting HR stream data
        #         if "heartrate" in activityStreams.keys():
        #             HRStream = activityStreams["heartrate"].data
        #         else:
        #             HRStream = [0]
        #
        #         # predict intensity of the run
        #         predictedIntensity = kmeans_predictor.predict(
        #             distance, elevationGain, elapsedTime, averageHeartRate
        #         )
        #
        #         # setup the data to show on webpage
        #         dataToBeAdded = {
        #                 "average_heart_rate": averageHeartRate,
        #                 "distance": distance,
        #                 "elapsed_time": elapsedTime,
        #                 "elevation_gain": elevationGain,
        #                 "predicted_intensity": predictedIntensity,
        #                 "activity_name": activityName,
        #                 "HRStream": HRStream
        #             }
        #
        #         activityDataToDisplay.append(dataToBeAdded)
        #
        #         # insert data into mongoDB
        #         self.__dbClient.insertRunningData(stravaAthlete.id, garminClient.get_activity(activityID).id, distance, elapsedTime, elevationHigh, elevationLow, predictedIntensity, averageHeartRate, activityName, stravaAthlete.firstname, HRStream)
        #
        #         # insert data into Redis
        #         self.__cacheClient.insertJSONData(600, self.__cacheClient.createKey(activityID), dataToBeAdded)
        #     else:
        #         # get data from redis cloud cache instead of mongoDB
        #         dataToBeAdded = self.__cacheClient.getDataFromKey(self.__cacheClient.createKey(activityID))
        #
        #         if dataToBeAdded is not None:
        #             # data formatting  
        #             activityDataToDisplay.append(
        #                 {
        #                     "average_heart_rate": dataToBeAdded["average_heart_rate"],
        #                     "distance": dataToBeAdded["distance"],
        #                     "elapsed_time": dataToBeAdded["elapsed_time"],
        #                     "elevation_gain": dataToBeAdded["elevation_gain"],
        #                     "predicted_intensity": dataToBeAdded["predicted_intensity"],
        #                     "activity_name": dataToBeAdded["activity_name"],
        #                     "HRStream": dataToBeAdded["HRStream"]
        #                 }
        #             )
        #             print("Data Entry already exists on redis DB!")
        #             print("Getting data from redis DB!")
        #         else:
        #             print("Data does not exist on redis DB! ")
        #             print("Getting data from mongoDB!")
        #
        #             dataToBeAdded = self.__dbClient.retrieveRunningData(activityID, stravaAthlete.id)
        #
        #             if dataToBeAdded is not None:
        #                 jsonRedisData = {
        #                     "average_heart_rate": dataToBeAdded["AVGHR"],
        #                     "distance": dataToBeAdded["Distance"],
        #                     "elapsed_time": dataToBeAdded["ElapsedTime"],
        #                     "elevation_gain": round((dataToBeAdded["ElevationH"] - dataToBeAdded["ElevationL"]), 1),
        #                     "predicted_intensity": dataToBeAdded["PredictedIntensity"],
        #                     "activity_name": dataToBeAdded["ActivityName"],
        #                     "HRStream": dataToBeAdded["HRStream"]
        #                     }
        #
        #                 activityDataToDisplay.append(
        #                     {
        #                         "average_heart_rate": dataToBeAdded["AVGHR"],
        #                         "distance": dataToBeAdded["Distance"],
        #                         "elapsed_time": dataToBeAdded["ElapsedTime"],
        #                         "elevation_gain": round((dataToBeAdded["ElevationH"] - dataToBeAdded["ElevationL"]), 1),
        #                         "predicted_intensity": dataToBeAdded["PredictedIntensity"],
        #                         "activity_name": dataToBeAdded["ActivityName"]
        #                     }
        #                 )
        #                 # insert into redis database
        #                 self.__cacheClient.insertJSONData(600, self.__cacheClient.createKey(activityID), jsonRedisData)
        #                 print("Inserting data into redis DB!")
        #             else:
        #                 print("Data retrieved is None! Error...")
        #
        
