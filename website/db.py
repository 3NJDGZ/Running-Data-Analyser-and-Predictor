from flask_pymongo import PyMongo
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

