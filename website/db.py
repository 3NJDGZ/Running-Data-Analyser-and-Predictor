from flask_pymongo import PyMongo

class DB:
    def __init__(self, app, mongoURI):
        self.__mongoURI = mongoURI
        self.__DB = PyMongo()
        self.__app = app
        self.configureConnection()

    def getMongoURI(self):
        return self.__mongoURI
    
    def configureConnection(self):
        self.__DB.init_app(self.__app) 

    def insertRunningData(self, athleteID, activityID, distance, time, elevationH, elevationL, predictedIntensity, avgHR):
        dataToBeAdded = {"AthleteID": athleteID,
                         "ActivityID": activityID,
                         "Distance": distance,
                         "Time": time,
                         "ElevationH": elevationH,
                         "ElevationL": elevationL,
                         "PredictedIntensity": predictedIntensity,
                         "AVGHR": avgHR}
        RDATCollection = self.__DB.db.RDAT
        RDATCollection.insert_one(dataToBeAdded)


