import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# import necessary modules
from flask import render_template
from website.baseView import baseView
from stravalib import Client
from kMeansClustering import kmeans_predictor
import json
import matplotlib

matplotlib.use("Agg")  # Use a non-interactive backend
import matplotlib.pyplot as plt


# wrap auth routes in a class for OOP
class dataVisualsRoutes(baseView):
    def __init__(self, flaskApp):
        super().__init__(flaskApp)
        ## setup necessary variables
        # self.__client_id, self.__client_secret = (
        #    open("client_secrets.txt").read().strip().split(",")
        # )
        # self.__request_scope = ["read_all", "profile:read_all", "activity:read_all"]
        # self.__redirect_url = (
        #    "http://127.0.0.1:5000/authentication"  # this is redirect url
        # )

    def _setupRoutes(self):
        # setup routes
        @self._flaskApp.route("/datavisualisation")
        def data_visualisation():
            with open(r"website/token.json", "r") as f:
                access_token_file = json.load(f)

            client = Client(access_token=access_token_file["access_token"])

            activities = client.get_activities()  # gets the athlete's activities
            activity_ids = []  # get the unique ids of each activity so we can get the 'detailed' activities object via the 'get_activity()' function
            activity_data = []  # will be used to hold data
            for activity in activities:
                # check if the activity is a run
                if client.get_activity(activity.id).distance != 0:
                    activity_ids.append(activity.id)

            # will need to change this, abstract it to another object as we our doing data harvesting twice therefore using too much API calls as this code is also repeated in auth.py
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

            activity_streams = client.get_activity_streams(
                activity_ids[1], types=["heartrate"], resolution="low"
            )

            if "heartrate" in activity_streams.keys():
                heart_rate_data = activity_streams["heartrate"].data
                # print("Heart Rate Data: ", heart_rate_data)
                heart_rate_data = sorted(heart_rate_data)
                zone1 = len([hr for hr in heart_rate_data if 0 <= hr <= 120])
                zone2 = len([hr for hr in heart_rate_data if 121 <= hr <= 140])
                zone3 = len([hr for hr in heart_rate_data if 141 <= hr <= 160])
                zone4 = len([hr for hr in heart_rate_data if 161 <= hr <= 180])
                zone5 = len([hr for hr in heart_rate_data if 181 <= hr <= 210])
                # Create lists for values and labels
                zones_value = [zone1, zone2, zone3, zone4, zone5]
                zones_title = [
                    "Zone 1 (0-120 bpm)",
                    "Zone 2 (121-140 bpm)",
                    "Zone 3 (141-160 bpm)",
                    "Zone 4 (161-180 bpm)",
                    "Zone 5 (181-210 bpm)",
                ]

                # Create the pie chart
                plt.figure(figsize=(8, 8))

                # Define custom colors for better distinction
                colors = [
                    "#ff9999",
                    "#66b3ff",
                    "#99ff99",
                    "#ffcc99",
                    "#c2c2f0",
                ]  # Customize colors here

                # Explode the slices for better visibility
                explode = (
                    0.1,
                    0,
                    0,
                    0,
                    0,
                )  # Only "explode" the first slice (Zone 1)

                wedges, texts, autotexts = plt.pie(
                    zones_value,
                    labels=None,  # Set labels to None for the pie chart
                    autopct="%1.1f%%",
                    startangle=140,
                    colors=colors,
                    explode=explode,
                )

                # Adding the legend outside the pie chart
                plt.legend(
                    wedges,
                    zones_title,
                    title="Heart Rate Zones",
                    loc="center left",
                    bbox_to_anchor=(1, 0, 0.5, 1),
                )

                # Improve aesthetics
                plt.title("Heart Rate Zones Distribution", fontsize=16)
                plt.axis(
                    "equal"
                )  # Equal aspect ratio ensures the pie chart is circular.

                # Save and show the plot
                plt.savefig(
                    "website/static/statisticalGraphsAndCharts/heart_rate_zones.png",
                    bbox_inches="tight",
                )
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
