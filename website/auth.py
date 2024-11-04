import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# import necessary modules
from flask import Blueprint, render_template, request
from website.baseView import baseView
from stravalib import Client, strava_model
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

            # creates auth url
            url = client.authorization_url(
                client_id=self.__client_id,
                redirect_uri=self.__redirect_url,
                scope=self.__request_scope,
                approval_prompt="auto",
            )

            return render_template("login.html", authorize_url=url)

        @self._flaskApp.route("/authentication")
        def logged_in():  # just shows their auth token, will show their data or something in the future
            code = request.args.get("code")
            client = Client()

            # gets access token
            access_token = client.exchange_code_for_token(
                client_id=self.__client_id,
                client_secret=self.__client_secret,
                code=code,
            )

            # Save the token response as a JSON file
            with open(r"website\token.json", "w") as f:
                json.dump(access_token, f)

            # gets the athlete
            activities = client.get_activities()
            activity_ids = []  # get the unique ids of each activity so we can get the 'detailed' activities object via the 'get_activity()' function
            activity_data = []
            for activity in activities:
                activity_ids.append(activity.id)
                # print(f"\nActivity ID: {activity.id}")
                # print(f"Distance (m): {activity.distance}")
                # print(f"Max Speed (m/s): {activity.max_speed}")
                # print(f"Elapsed Time (s): {activity.elapsed_time}")

            for x in range(3):
                averageHeartRate = client.get_activity(
                    activity_ids[x]
                ).average_heartrate
                distance = client.get_activity(activity_ids[x]).distance
                elapsedTime = client.get_activity(activity_ids[x]).elapsed_time
                elevationHigh = client.get_activity(activity_ids[x]).elev_high
                elevationLow = client.get_activity(activity_ids[x]).elev_low
                elevationGain = elevationHigh - elevationLow
                print(averageHeartRate, distance, elapsedTime, elevationGain)

                activity_data.append(
                    {
                        "average_heart_rate": averageHeartRate,
                        "distance": distance,
                        "elapsed_time": elapsedTime,
                        "elevation_gain": elevationGain,
                    }
                )

                if distance != 0:
                    kmeans_predictor.predict(
                        distance, elevationGain, elapsedTime, averageHeartRate
                    )

                activity_streams = client.get_activity_streams(
                    activity_ids[x], types=["heartrate"], resolution="high"
                )

                if "heartrate" in activity_streams.keys():
                    heart_rate_data = activity_streams["heartrate"].data
                    print("Heart Rate Data: ", heart_rate_data)
                else:
                    print("Heart rate data not available for this activity.")
            avg_hr = client.get_activity(activity_ids[x]).average_heartrate
            print(f"Avg Heart Rate: {avg_hr}")

            strava_athlete = client.get_athlete()

            return render_template(
                "login_results.html",
                athlete=strava_athlete,
                access_token=access_token,
                activity_data=activity_data,
            )

        @self._flaskApp.route("/datavisualisation")
        def data_visualisation():
            with open(r"website\token.json", "r") as f:
                token_response_refresh = json.load(f)

            client = Client()

            refresh_response = client.refresh_access_token(
                client_id=self.__client_id,
                client_secret=self.__client_secret,
                refresh_token=token_response_refresh[
                    "refresh_token"
                ],  # Stored in your JSON file
            )

            activities = client.get_activities()
            activity_ids = []  # get the unique ids of each activity so we can get the 'detailed' activities object via the 'get_activity()' function
            activity_data = []
            for activity in activities:
                activity_ids.append(activity.id)
                # print(f"\nActivity ID: {activity.id}")
                # print(f"Distance (m): {activity.distance}")
                # print(f"Max Speed (m/s): {activity.max_speed}")
                # print(f"Elapsed Time (s): {activity.elapsed_time}")

            for x in range(3, 5):
                averageHeartRate = client.get_activity(
                    activity_ids[x]
                ).average_heartrate
                distance = client.get_activity(activity_ids[x]).distance
                elapsedTime = client.get_activity(activity_ids[x]).elapsed_time
                elevationHigh = client.get_activity(activity_ids[x]).elev_high
                elevationLow = client.get_activity(activity_ids[x]).elev_low
                elevationGain = elevationHigh - elevationLow
                print(averageHeartRate, distance, elapsedTime, elevationGain)

                activity_data.append(
                    {
                        "average_heart_rate": averageHeartRate,
                        "distance": distance,
                        "elapsed_time": elapsedTime,
                        "elevation_gain": elevationGain,
                    }
                )

            return render_template(
                "data_visuals.html",
                activity_data=activity_data,
            )
