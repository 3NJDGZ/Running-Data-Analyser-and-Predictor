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
class dataVisualsRoutes(baseView):
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
        @self._flaskApp.route("/datavisualisation")
        def data_visualisation():
            with open(r"token.json", "r") as f:
                access_token_file = json.load(f)

            client = Client(access_token=access_token_file["access_token"])

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
