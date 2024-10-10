from flask import Blueprint, render_template, request
from stravalib import Client

auth = Blueprint('auth', __name__)

# setup necessary variables
client_id, client_secret = open("client_secrets.txt").read().strip().split(",")
request_scope = ["read_all", "profile:read_all", "activity:read_all"]
redirect_url = "http://127.0.0.1:5000/strava-oauth" # this is redirect url

# setup routes
@auth.route("/")
def login():
    client = Client()
    # creates auth url 
    url = client.authorization_url(
    client_id=client_id,
    redirect_uri=redirect_url,
    scope=request_scope,
    approval_prompt="auto"
    )
    return render_template('login.html', authorize_url = url)

@auth.route("/strava-oauth")
def logged_in():
    code = request.args.get("code")
    client = Client()
    # gets access token
    access_token = client.exchange_code_for_token(
        client_id=client_id,
        client_secret=client_secret,
        code=code
    )

    # activity = client.get_activity(0)

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
        avg_hr = client.get_activity(activity_ids[x]).average_heartrate
        print(f"Avg Heart Rate: {client.get_activity(activity_ids[x]).average_heartrate}")
    
    strava_athlete = client.get_athlete()

    return render_template(
        "login_results.html",
        athlete=strava_athlete,
        access_token=access_token,
    )