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
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt



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

                activity_streams = client.get_activity_streams(activity_ids[1], types=['heartrate'], resolution='low')

                if 'heartrate' in activity_streams.keys():
                    heart_rate_data = activity_streams['heartrate'].data
                    # print("Heart Rate Data: ", heart_rate_data)
                    heart_rate_data = sorted(heart_rate_data)
                    zone1 = len([hr for hr in heart_rate_data if 0 <= hr <= 120])
                    zone2 = len([hr for hr in heart_rate_data if 121 <= hr <= 140])
                    zone3 = len([hr for hr in heart_rate_data if 141 <= hr <= 160])
                    zone4 = len([hr for hr in heart_rate_data if 161 <= hr <= 180])
                    zone5 = len([hr for hr in heart_rate_data if 181 <= hr <= 210])
                    zones_value = [zone1, zone2, zone3, zone4, zone5]
                    zones_title = ['Zone 1', 'Zone 2', 'Zone 3', 'Zone 4', 'Zone 5']

                    plt.pie(zones_value, labels=zones_title)

                    plt.savefig("heart_rate_zones.png")
                    plt.show()
                else:
                    print("Heart rate data not available for this activity.")
                avg_hr = client.get_activity(activity_ids[1]).average_heartrate
                # print(f"Avg Heart Rate: {avg_hr}")

            return render_template(
                "data_visuals.html",
                activity_data=activity_data,
                avg_hr=avg_hr,
            )
