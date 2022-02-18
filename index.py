from flask import Flask
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import traceback
import datetime
import google_auth_oauthlib.flow
from os import environ
import flask
from flask import render_template
import json

app = Flask(__name__,
            static_url_path='',
            static_folder='static/')
app.secret_key = environ["FLASK_SECRET_KEY"]

@app.route('/')
def home():
    render_template('index.html')

@app.route('/create')
def home():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    credentials = Credentials(**flask.session['credentials'])
    calendar = build("calendar", "v3", credentials=credentials)


    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time



    # set review events
    day0 = datetime.datetime.today() - datetime.timedelta(days=1)
    day1 = (day0 + datetime.timedelta(days=1)).isoformat() + 'Z'
    day2 = (day0 + datetime.timedelta(days=3)).isoformat() + 'Z'
    day3 = (day0 + datetime.timedelta(days=6)).isoformat() + 'Z'
    day4 = (day0 + datetime.timedelta(days=13)).isoformat() + 'Z'
    day5 = (day0 + datetime.timedelta(days=27)).isoformat() + 'Z'
    day6 = (day0 + datetime.timedelta(days=55)).isoformat() + 'Z'
    day7 = (day0 + datetime.timedelta(days=83)).isoformat() + 'Z'
    day8 = (day0 + datetime.timedelta(days=111)).isoformat() + 'Z'
    day9 = (day0 + datetime.timedelta(days=139)).isoformat() + 'Z'
    for day in [day1, day2, day3, day4, day5, day6, day7, day8, day9]:
        event = {
            'summary': 'testpoop',
            'start': {
                'dateTime': day,
            },
            'end': {
                'dateTime': day,
            }
        }
        # Call the Calendar API
        calendar.events().insert(calendarId='primary', sendNotifications=True, body=event).execute()

    return 'ok'



@app.route('/authorize')
def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=json.loads(environ["CLIENT_SECRET_JSON"]),
        scopes=['https://www.googleapis.com/auth/calendar.events'])
    flow.redirect_uri = 'https://review-planner.vercel.app/oauthcallback'
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')
    flask.session['state'] = state
    return flask.redirect(authorization_url)

@app.route('/oauthcallback')
def oauthcallback():
    print("hello")
    try:
        state = flask.session['state']
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            client_config=json.loads(environ["CLIENT_SECRET_JSON"]),
            scopes=['https://www.googleapis.com/auth/calendar.events'],
            state=state)
        flow.redirect_uri = flask.url_for('oauthcallback', _external=True)

        authorization_response = flask.request.url
        flow.fetch_token(authorization_response=authorization_response)

        # Store the credentials in the session.
        # ACTION ITEM for developers:
        #     Store user's access and refresh tokens in your data store if
        #     incorporating this code into your real app.
        credentials = flow.credentials
        flask.session['credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}

        return flask.redirect(flask.url_for('home'))
    except Exception as e:
        print(traceback.format_exc())
        raise e

@app.route('/portfolio')
def portfolio():
    return 'Portfolio Page Route'