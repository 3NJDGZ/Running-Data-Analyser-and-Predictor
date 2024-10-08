from flask import Flask, render_template, request, url_for
from stravalib import Client

# create flask application
app = Flask(__name__)

# setup necessary variables
client_id, client_secret = open("client_secrets.txt").read().strip().split(",")
request_scope = ["read_all", "profile:read_all", "activity:read_all"]
redirect_url = "http://127.0.0.1:5000/strava-oauth" # this is redirect url

# setup routes
@app.route("/")
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

@app.route("/strava-oauth")
def logged_in():
    code = request.args.get("code")
    client = Client()
    # gets access token
    access_token = client.exchange_code_for_token(
        client_id=client_id,
        client_secret=client_secret,
        code=code
    )

    # gets the athlete
    strava_athlete = client.get_athlete()

    return render_template(
        "login_results.html",
        athlete=strava_athlete,
        access_token=access_token,
    )

if __name__ == "__main__":
    app.run(debug=True)