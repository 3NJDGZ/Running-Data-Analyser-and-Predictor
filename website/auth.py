import sys
import os

from flask.helpers import redirect
import garminconnect as garmin 
from garminconnect import Garmin, GarminConnectAuthenticationError, GarminConnectConnectionError, GarminConnectTooManyRequestsError
from garth.exc import GarthHTTPError

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# import necessary modules
from flask import render_template, request, url_for
from website.baseView import baseView
from website.cachingService.cachingSystem import CachingSystem 
from stravalib import Client
import json

# wrap auth routes in a class for OOP
class authRoutes(baseView):
    def __init__(self, flaskApp, cachingSystem: CachingSystem):
        super().__init__(flaskApp)
        self.__cachingSystem = cachingSystem
        self.__tokenstore = os.getenv("GARMINTOKENS") or "~/.garminconnect"
        self.__garminClient = Garmin()
       
    def _setupRoutes(self):
        # setup routes
        @self._flaskApp.route("/", methods=["GET", "POST"])
        def login():  
            usrFullName = ""
            error = False

            if request.method == "POST":
                email = request.form.get("email")
                pwd = request.form.get("password")
                remember = request.form.get("remember")
                if remember is None:
                    remember = "off"
                print(f"Email: {email}, Password: {pwd}, Remember: {remember}")
                try:
                    self.__garminClient = Garmin(email=email, password=pwd)
                    self.__garminClient.login()
                    self.__garminClient.garth.dump(self.__tokenstore)
                    usrFullName = self.__garminClient.get_full_name()
                    return redirect(url_for("logged_in", usrFullName = usrFullName)) 
                except (GarminConnectAuthenticationError, 
                        GarminConnectConnectionError, 
                        GarminConnectTooManyRequestsError, 
                        GarthHTTPError) as e:
                    print("Invalid login!")
                    print(f"Error encountered!\n---- Error Message ----\n{e}")
                    error = True
                    return render_template("login.html", usrFullName=usrFullName, error=error)
            else:
                return render_template("login.html", usrFullName=usrFullName, error=error)

        @self._flaskApp.route("/<usrFullName>")
        def logged_in(usrFullName):

            # gets all the activities, and filters them by if they are a running activity
            # activities = self.__garminClient.get_activities(0, 10)
            #
            # if activities is not None:
            #     for activity in activities:
            #         if activity['activityType']['typeId'] == 1:
            #             print(f"Activity ID: {activity['activityId']}\n")
            
            activityData = self.__cachingSystem.getActivityData(garminClient=self.__garminClient)

            return render_template(
                 "login_results.html",
                 athleteName = usrFullName,
                 activity_data=activityData,
            )
