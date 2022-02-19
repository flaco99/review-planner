from flask import Flask
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import traceback
import datetime
import google_auth_oauthlib.flow
from os import environ
import flask
from flask import render_template, request
import json

app = Flask(__name__,
            static_url_path='',
            static_folder='static/')
app.secret_key = environ["FLASK_SECRET_KEY"]

@app.route('/')
def home():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')
    credentials = Credentials(**flask.session['credentials'])
    calendar = build("calendar", "v3", credentials=credentials)
    try:
        calendar.events().list(calendarId='primary', maxResults=10).execute()
    except RefreshError:
        return flask.redirect('authorize')
    return render_template('index.html')

@app.route('/create', methods = ['POST'])
def create():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    credentials = Credentials(**flask.session['credentials'])
    calendar = build("calendar", "v3", credentials=credentials)

    eventname = request.form['eventname']

    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time



    # set review events

    # duration of event shrinks when days increase

    # set the first day
    day0 = datetime.datetime.today() - datetime.timedelta(days=1)

    maxdays = 60
    daysplus = 1
    intervalfactor = 3
    duration = 10
    while daysplus < maxdays:
        day = (day0 + datetime.timedelta(days=daysplus)).isoformat() + 'Z'
        event = {
            'summary': eventname,
            'start': {
                'dateTime': day,
            },
            'end': {
                'dateTime': day,
            }
        }
        # Call the Calendar API
        calendar.events().insert(calendarId='primary', sendNotifications=True, body=event).execute()

        # set to the next day
        daysplus = daysplus * intervalfactor
        duration = duration / 2

    return f"OK: {eventname}"


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