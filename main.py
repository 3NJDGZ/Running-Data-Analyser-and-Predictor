# import necessary classes and functions
from website import create_app
from website.views import viewRoutes
from website.auth import authRoutes
from website.dataVisuals import dataVisualsRoutes
from website.cachingService.cachingSystem import CachingSystem 
from website.cachingService.cachingClient import CacheClient
from website.cachingService.databaseClient import DatabaseClient

# get mongoURI from txt file
with open("mongoURI.txt", "r") as file:
    mongoURI = file.readline()  

# create flask wrapper
class flaskAppWrapper:
    def __init__(self, mongoURI):
        # create and setup the flask app
        self.__app = create_app()  
        self.__app.config["MONGO_URI"] = (mongoURI)
        self.__cachingSystem = CachingSystem(CacheClient(), DatabaseClient(self.__app, mongoURI))

        self.setupRoutes()  
        
    def setupRoutes(self):
        # create the different routes, and call their protected methods which are overridden from baseView abstract super class
        views = viewRoutes(self.__app)
        auth = authRoutes(self.__app, self.__cachingSystem)
        dataVisuals = dataVisualsRoutes(self.__app, self.__cachingSystem)
        views._setupRoutes()
        auth._setupRoutes()
        dataVisuals._setupRoutes()

    def run(self):
        self.__app.run(debug=True)

flaskAppWrapper = flaskAppWrapper(mongoURI)

if __name__ == "__main__":
    flaskAppWrapper.run()
