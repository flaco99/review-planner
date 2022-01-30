from flask import Flask
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import traceback
import datetime
import google_auth_oauthlib.flow
from os import environ
from flask import request
import flask
import json

app = Flask(__name__,
            static_url_path='',
            static_folder='static/')
app.secret_key = environ["A8CF5DBA1AF5B4A9DC137657C36A6"]



@app.route('/')
def home():
    try:
        # Use the client_secret.json file to identify the application requesting
        # authorization. The client ID (from that file) and access scopes are required.

        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            client_config=json.loads(environ["CLIENT_SECRET_JSON"]),
            scopes=['https://www.googleapis.com/auth/calendar.events'])

        # Indicate where the API server will redirect the user after the user completes
        # the authorization flow. The redirect URI is required. The value must exactly
        # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
        # configured in the API Console. If this value doesn't match an authorized URI,
        # you will get a 'redirect_uri_mismatch' error.
        flow.redirect_uri = 'https://review-planner.vercel.app/oauthcallback'

        # Generate URL for request to Google's OAuth 2.0 server.
        # Use kwargs to set optional request parameters.
        authorization_url, state = flow.authorization_url(
            # Enable offline access so that you can refresh an access token without
            # re-prompting the user for permission. Recommended for web server apps.
            access_type='offline',
            login_hint='naomi@neopatent.com',
            prompt='consent',
            # Enable incremental authorization. Recommended as a best practice.
            include_granted_scopes='true')
        flask.session['state'] = state
        return flask.redirect(authorization_url)
    except Exception as e:
        return str(traceback.format_exc())

@app.route('/oauthcallback')
def oauthcallback():
    try:
        # authcode = request.args.get('code')

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

        return "OK"
    except Exception as e:
        return str(traceback.format_exc())

@app.route('/dumdum/<idtoken>')
def about(idtoken):
    try:
        creds = Credentials(None, id_token=idtoken)
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        if not events:
            return 'No upcoming events found.'

        result = ""
        # Prints the start and name of the next 10 events
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            result += f"{start} {event['summary']}"
        return result
    except Exception as e:
        return str(traceback.format_exc())


@app.route('/portfolio')
def portfolio():
    return 'Portfolio Page Route'
