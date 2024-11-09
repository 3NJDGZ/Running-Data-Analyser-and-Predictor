# import necessary classes and functions
from website import create_app, createMongoDB
from website.views import viewRoutes
from website.auth import authRoutes
from website.dataVisuals import dataVisualsRoutes


# create flask wrapper
class flaskAppWrapper:
    def __init__(self):
        self.__app = create_app()  # creates flask application itself
        self.__mongoDB = createMongoDB(self.__app)
        self.setupRoutes()  # sets up the routes for the browser

    def setupRoutes(self):
        # create the different routes, and call their protected methods which are overridden from baseView abstract super class
        views = viewRoutes(self.__app)
        auth = authRoutes(self.__app)
        dataVisuals = dataVisualsRoutes(self.__app)
        views._setupRoutes()
        auth._setupRoutes()
        dataVisuals._setupRoutes()

    def run(self):
        self.__app.run(debug=True)


flaskAppWrapper = flaskAppWrapper()

if __name__ == "__main__":
    flaskAppWrapper.run()

