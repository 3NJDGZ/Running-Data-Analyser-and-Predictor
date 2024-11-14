from flask_pymongo import PyMongo
from pandas.core.frame import dataclasses_to_dicts
from kMeansClustering import kmeans_predictor

class DB:
    def __init__(self, app, mongoURI, cr):
        self.cr = cr # cache redis object 
        self.__mongoURI = mongoURI
        self.__DB = PyMongo()
        self.__app = app
        self.configureConnection()
        self.__RDATCollection = self.__DB.db.RDAT

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
                dataToBeAdded = {
                        "average_heart_rate": averageHeartRate,
                        "distance": distance,
                        "elapsed_time": elapsedTime,
                        "elevation_gain": elevationGain,
                        "predicted_intensity": predictedIntensity,
                        "activity_name": activityName
                    }

                activity_data.append(dataToBeAdded)

                self.insertRunningData(strava_athlete.id, client.get_activity(activityID).id, distance, elapsedTime, elevationHigh, elevationLow, predictedIntensity, averageHeartRate, activityName, strava_athlete.firstname, hrStream)
                print("Data inserted!")
                
                # insert data into Redis
                self.cr.insertJSONData(600, self.cr.createKey(activityID), dataToBeAdded)
            else:
                # get data from redis cloud cache instead of mongoDB
                dataToBeAdded = self.cr.getDataFromKey(self.cr.createKey(activityID))

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
                    dataToBeAdded = self.retrieveRunningData(activityID, strava_athlete.id)

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
                    self.cr.insertJSONData(600, self.cr.createKey(activityID), test)
                    print("Inserting data into redis DB!")

        return activity_data
        


