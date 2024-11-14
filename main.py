# import necessary classes and functions
from website import create_app
from website.views import viewRoutes
from website.auth import authRoutes
from website.dataVisuals import dataVisualsRoutes
from website.db import DB
from website.cacheRedis import cacheRedis

# get mongoURI from txt file
with open("mongoURI.txt", "r") as file:
    mongoURI = file.readline()  

# create flask wrapper
class flaskAppWrapper:
    def __init__(self, mongoURI):
        # create and setup the flask app
        self.__app = create_app()  
        self.__app.config["MONGO_URI"] = (mongoURI)

        self.__cacheRedis = cacheRedis()

        # Setup the mongoDB connection 
        self.__mongoDB = DB(self.__app, mongoURI, cacheRedis())
        self.__mongoDB.configureConnection()

        self.setupRoutes()  
        
    def setupRoutes(self):
        # create the different routes, and call their protected methods which are overridden from baseView abstract super class
        views = viewRoutes(self.__app)
        auth = authRoutes(self.__app, self.__mongoDB, self.__cacheRedis)
        dataVisuals = dataVisualsRoutes(self.__app, self.__mongoDB, self.__cacheRedis)
        views._setupRoutes()
        auth._setupRoutes()
        dataVisuals._setupRoutes()

    def run(self):
        self.__app.run(debug=True)

flaskAppWrapper = flaskAppWrapper(mongoURI)

if __name__ == "__main__":
    flaskAppWrapper.run()
