# import necessary classes and functions
from website import create_app
from website.views import viewRoutes
from website.auth import authRoutes
from website.dataVisuals import dataVisualsRoutes
from website.cachingService.cachingSystem import CachingSystem 
from website.cachingService.cachingClient import CacheClient
from website.cachingService.databaseClient import DatabaseClient
from website.client.GarminUserClient import GarminUserClient

# get mongoURI from txt file
with open("mongoURI.txt", "r") as file:
    mongoURI = file.readline()  

# create flask wrapper
class flaskAppWrapper:
    def __init__(self, mongoURI):
        # create and setup the flask app
        self.__app = create_app()  
        self.__app.config["MONGO_URI"] = (mongoURI)
        self.__app.config["MONGO_MAX_POOL_SIZE"] = 10  # Maximum connections in the pool
        self.__app.config["MONGO_MIN_POOL_SIZE"] = 1   # Minimum connections in the pool
        self.__cachingSystem = CachingSystem(CacheClient(), DatabaseClient(self.__app, mongoURI))
        self.__garminUserClient = GarminUserClient()

        self.setupRoutes()  
        
    def setupRoutes(self):
        # create the different routes, and call their protected methods which are overridden from baseView abstract super class
        views = viewRoutes(self.__app)
        auth = authRoutes(self.__app, self.__cachingSystem, self.__garminUserClient)
        dataVisuals = dataVisualsRoutes(self.__app, self.__cachingSystem, self.__garminUserClient)
        views._setupRoutes()
        auth._setupRoutes()
        dataVisuals._setupRoutes()

    def run(self):
        self.__app.run(port=8000, debug=True)

flaskApp = flaskAppWrapper(mongoURI)

if __name__ == "__main__":
    flaskApp.run()
