from flask_pymongo import PyMongo
from kMeansClustering import kmeans_predictor
import redis

class DB:
    def __init__(self, app, mongoURI):
        self.__mongoURI = mongoURI
        self.__DB = PyMongo()
        self.__app = app
        self.configureConnection()
        self.__RDATCollection = self.__DB.db.RDAT

        self.__redis = redis.Redis(host='localhost', port=6379, decode_responses=True)


    def getMongoURI(self):
        return self.__mongoURI
    
    def configureConnection(self):
        self.__DB.init_app(self.__app) 

    def retrieveRunningData(self, activityID, athleteID):
        cursor = self.__RDATCollection.find({"ActivityID": activityID,
                                             "AthleteID": athleteID})
        for doc in cursor:
            return doc

    def retrieveAthleteActivities(self, athleteID):
        cursor = self.__RDATCollection.find({"AthleteID": athleteID})
        docs = []

        for doc in cursor:
            docs.append(doc)

        return docs

    def insertRunningData(self, athleteID, activityID, distance, time, elevationH, elevationL, predictedIntensity, avgHR, activityName, athleteFirstName, hrStream):
        dataToBeAdded = {"AthleteID": athleteID,
                         "AthleteFirstName": athleteFirstName,
                         "ActivityID": activityID,
                         "ActivityName": activityName,
                         "Distance": distance,
                         "ElapsedTime": time,
                         "ElevationH": elevationH,
                         "ElevationL": elevationL,
                         "PredictedIntensity": predictedIntensity,
                         "AVGHR": avgHR,
                         "HRStream": hrStream}

        self.__RDATCollection.insert_one(dataToBeAdded)

    def getActivityData(self, activity_ids, client, strava_athlete, activity_data):
        # check if data entry already exists in mongoDB, if not then insert into database
        for activityID in activity_ids:
            if self.retrieveRunningData(activityID, strava_athlete.id) is None:
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
                activity_data.append(
                    {
                        "average_heart_rate": averageHeartRate,
                        "distance": distance,
                        "elapsed_time": elapsedTime,
                        "elevation_gain": elevationGain,
                        "predicted_intensity": predictedIntensity,
                        "activity_name": activityName
                    }
                )

                self.insertRunningData(strava_athlete.id, client.get_activity(activityID).id, distance, elapsedTime, elevationHigh, elevationLow, predictedIntensity, averageHeartRate, activityName, strava_athlete.firstname, hrStream)
                print("Data inserted!")
            else:
                dataToBeAdded = self.retrieveRunningData(activityID, strava_athlete.id)

                # data formatting  
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
                print("Data Entry already exists!")

        return activity_data
        


