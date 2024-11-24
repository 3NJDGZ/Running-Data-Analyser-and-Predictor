from flask_pymongo import PyMongo

class DatabaseClient:
    def __init__(self, app, mongoURI):
        self.__mongoURI = mongoURI
        self.__databaseClient = PyMongo()
        self.__app = app
        self.configureConnection()
        self.__RDATCollection = self.__databaseClient.db.RDAT

    def getMongoURI(self):
        return self.__mongoURI
    
    def configureConnection(self):
        self.__databaseClient.init_app(self.__app) 

    def retrieveRunningData(self, activityID):
        cursor = self.__RDATCollection.find({"activityID": activityID})

        for doc in cursor:
            return doc

    def retrieveAthleteActivities(self, athleteID):
        cursor = self.__RDATCollection.find({"athleteID": athleteID})
        docs = []

        for doc in cursor:
            docs.append(doc)

        return docs

    def insertRunningData(self, athleteID, activityID, distanceRan, elapsedTime, elevationGain, predictedIntensity, averageHR, activityName, athleteName, HRStream):
        dataToBeAdded = {"athleteID": athleteID,
                         "athleteName": athleteName,
                         "activityID": activityID,
                         "activityName": activityName,
                         "distanceRan": distanceRan,
                         "elapsedTime": elapsedTime,
                         "elevationGain": elevationGain,
                         "predictedIntensity": predictedIntensity,
                         "averageHR": averageHR,
                         "HRStream": HRStream}

        self.__RDATCollection.insert_one(dataToBeAdded)
