import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# import necessary modules
from flask import render_template, request
from website.baseView import baseView
from stravalib import Client
from kMeansClustering import kmeans_predictor
import json


# wrap auth routes in a class for OOP
class authRoutes(baseView):
    def __init__(self, flaskApp):
        super().__init__(flaskApp)
        # setup necessary variables
        self.__client_id, self.__client_secret = (
            open("client_secrets.txt").read().strip().split(",")
        )
        self.__request_scope = ["read_all", "profile:read_all", "activity:read_all"]
        self.__redirect_url = (
            "http://127.0.0.1:5000/authentication"  # this is redirect url
        )

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

            activities = client.get_activities()  # gets the athlete's activities
            activity_ids = []  # get the unique ids of each activity so we can get the 'detailed' activities object via the 'get_activity()' function
            activity_data = []  # will be used to hold data
            for activity in activities:
                # check if the activity is a run
                if client.get_activity(activity.id).distance != 0:
                    activity_ids.append(activity.id)

            for x in range(3):
                averageHeartRate = client.get_activity(
                    activity_ids[x]
                ).average_heartrate
                distance = client.get_activity(activity_ids[x]).distance
                elapsedTime = client.get_activity(activity_ids[x]).elapsed_time
                elevationHigh = client.get_activity(activity_ids[x]).elev_high
                elevationLow = client.get_activity(activity_ids[x]).elev_low
                elevationGain = elevationHigh - elevationLow
                elevationGain = round(elevationGain, 1)
                print(averageHeartRate, distance, elapsedTime, elevationGain)

                # predict intensity of the run
                predictedIntensity = kmeans_predictor.predict(
                    distance, elevationGain, elapsedTime, averageHeartRate
                )

                # setup the data
                activity_data.append(
                    {
                        "average_heart_rate": averageHeartRate,
                        "distance": distance,
                        "elapsed_time": elapsedTime,
                        "elevation_gain": elevationGain,
                        "predicted_intensity": predictedIntensity,
                    }
                )

            print(len(activity_data))

            # activity_streams = client.get_activity_streams(
            #     activity_ids[x], types=["heartrate"], resolution="low"
            # )

            # if "heartrate" in activity_streams.keys():
            #     heart_rate_data = activity_streams["heartrate"].data
            #     print("Heart Rate Data: ", heart_rate_data)
            # else:
            #     print("Heart rate data not available for this activity.")
            #
            # avg_hr = client.get_activity(activity_ids[x]).average_heartrate
            # print(f"Avg Heart Rate: {avg_hr}")

            strava_athlete = client.get_athlete()

            return render_template(
                "login_results.html",
                athlete=strava_athlete,
                access_token=access_token,
                activity_data=activity_data,
            )
