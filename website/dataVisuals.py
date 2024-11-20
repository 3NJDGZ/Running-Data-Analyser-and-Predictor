import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# import necessary modules
from flask import render_template
from website.baseView import baseView
from stravalib import Client
from website.cachingService.cachingSystem import CachingSystem
import json
import matplotlib

matplotlib.use("Agg")  # Use a non-interactive backend
import matplotlib.pyplot as plt


# wrap auth routes in a class for OOP
class dataVisualsRoutes(baseView):
    def __init__(self, flaskApp, cachingSystem: CachingSystem):
        super().__init__(flaskApp)
        self.__cachingSystem = cachingSystem

    def createHRPieChart(self, formmattedHRData):
        # create the figure
        heartRateData = formmattedHRData 
        zone1 = len([hr for hr in heartRateData if 0 <= hr <= 120])
        zone2 = len([hr for hr in heartRateData if 121 <= hr <= 140])
        zone3 = len([hr for hr in heartRateData if 141 <= hr <= 160])
        zone4 = len([hr for hr in heartRateData if 161 <= hr <= 180])
        zone5 = len([hr for hr in heartRateData if 181 <= hr <= 210])

        # Create lists for values and labels
        zonesValue = [zone1, zone2, zone3, zone4, zone5]
        zonesTitle = [
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

        wedges = plt.pie(
            zonesValue,
            labels=None,  # Set labels to None for the pie chart
            autopct="%1.1f%%",
            startangle=140,
            colors=colors,
            explode=explode,
        )

        # Adding the legend outside the pie chart
        plt.legend(
            wedges,
            zonesTitle,
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

    def _setupRoutes(self):
        # setup routes
        @self._flaskApp.route("/datavisualisation")
        def data_visualisation():
            with open(r"website/token.json", "r") as f:
                accessTokenFile = json.load(f)

            # Create client object again to retain session
            client = Client(access_token=accessTokenFile["access_token"])
            stravaAthlete = client.get_athlete()
            activityData = self.__cachingSystem.getActivityData(client)
            HRStreamData = []
            formattedHRStreamData = []
            for activity in activityData:
                HRStreamData.append(activity["HRStream"])

            # Format the HR stream data into a singular array
            for stream in HRStreamData:
                formattedHRStreamData = formattedHRStreamData + stream

            formattedHRStreamData.sort()

            self.createHRPieChart(formattedHRStreamData)
            
            return render_template(
                "data_visuals.html",
                activity_data=activityData,
            )
