# import necessary modules
from flask import Blueprint, render_template, request
from website.baseView import baseView
from stravalib import Client, strava_model

# wrap auth routes in a class for OOP
class authRoutes(baseView):
    def __init__(self, flaskApp):
        super().__init__(flaskApp)
        # setup necessary variables
        self.__client_id, self.__client_secret = open("client_secrets.txt").read().strip().split(",")
        self.__request_scope = ["read_all", "profile:read_all", "activity:read_all"]
        self.__redirect_url = "http://127.0.0.1:5000/authentication" # this is redirect url
    
    def _setupRoutes(self):
        # setup routes
        @self._flaskApp.route("/")
        def login(): # shows user a prompt to connect to strava
            client = Client()

            # creates auth url 
            url = client.authorization_url(
            client_id=self.__client_id,
            redirect_uri=self.__redirect_url,
            scope=self.__request_scope,
            approval_prompt="auto"
            )

            return render_template('login.html', authorize_url = url)

        @self._flaskApp.route("/authentication")
        def logged_in(): # just shows their auth token, will show their data or something in the future
            code = request.args.get("code")
            client = Client()
            
            # gets access token
            access_token = client.exchange_code_for_token(
                client_id=self.__client_id,
                client_secret=self.__client_secret,
                code=code
            )

            # gets the athlete
            activities = client.get_activities()
            activity_ids = [] # get the unique ids of each activity so we can get the 'detailed' activities object via the 'get_activity()' function
            for activity in activities:
                activity_ids.append(activity.id)
                # print(f"\nActivity ID: {activity.id}")
                # print(f"Distance (m): {activity.distance}")
                # print(f"Max Speed (m/s): {activity.max_speed}")
                # print(f"Elapsed Time (s): {activity.elapsed_time}")

            for x in range(len(activity_ids)):
                activity_streams = client.get_activity_streams(activity_ids[x], types=['heartrate'], resolution='high')

                if 'heartrate' in activity_streams.keys():
                    heart_rate_data = activity_streams['heartrate'].data
                    print("Heart Rate Data: ", heart_rate_data)
                else:
                    print("Heart rate data not available for this activity.")
                # avg_hr = client.get_activity(activity_ids[x]).average_heartrate
                # print(f"Avg Heart Rate: {avg_hr}")
            
            # testStream  = strava_model.HeartrateStream.model_dump(mode='json')

            # print(testStream)

            strava_athlete = client.get_athlete()

            return render_template(
                "login_results.html",
                athlete=strava_athlete,
                access_token=access_token,
            )