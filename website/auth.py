import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# import necessary modules
from flask import render_template, request
from website.baseView import baseView
from stravalib import Client
import json


# wrap auth routes in a class for OOP
class authRoutes(baseView):
    def __init__(self, flaskApp, mongoDB, cacheRedis):
        super().__init__(flaskApp)
        self.__mongoDB = mongoDB
        self.__cacheRedis = cacheRedis

        # setup necessary variables
        self.__client_id, self.__client_secret = (open("client_secrets.txt").read().strip().split(","))
        self.__request_scope = ["read_all", "profile:read_all", "activity:read_all"]
        self.__redirect_url = ("http://127.0.0.1:5000/authentication")

    def _setupRoutes(self):
        # setup routes
        @self._flaskApp.route("/")
        def login():  # shows user a prompt to connect to strava
            client = Client()

            # creates authentication url
            url = client.authorization_url(
                client_id=self.__client_id,
                redirect_uri=self.__redirect_url,
                scope=self.__request_scope,
                approval_prompt="auto",
            )

            return render_template("login.html", authorize_url=url)

        @self._flaskApp.route("/authentication")
        def logged_in():
            authCode = request.args.get("code")
            print(f"Authorization Code: {authCode}")
            client = Client()

            # exchanges authCode for access token in order to access athlete data
            access_token = client.exchange_code_for_token(
                client_id=self.__client_id,
                client_secret=self.__client_secret,
                code=authCode,
            )

            # Save the token response as a JSON file
            with open(r"website/token.json", "w") as f:
                json.dump(access_token, f)

            strava_athlete = client.get_athlete()
            activities = client.get_activities(None, None, 15) 
            activity_ids = []  # get the unique ids of each activity so we can get the 'detailed' activities object via the 'get_activity()' function
            activity_data = []  # will be used to hold data
            for activity in activities:
                rst = activity.sport_type # relaxed sport type
                if rst.root == "Run" and len(activity_ids) <= 4:
                    print(activity.id)
                    activity_ids.append(activity.id)
            
            activity_data = self.__mongoDB.getActivityData(activity_ids, client, strava_athlete, activity_data)

            return render_template(
                "login_results.html",
                athlete=strava_athlete,
                access_token=access_token,
                activity_data=activity_data,
            )
