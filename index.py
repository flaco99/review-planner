from flask import Flask
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import traceback
import datetime

app = Flask(__name__,
            static_url_path='',
            static_folder='../static')


@app.route('/')
def home():
    try:
        return app.send_static_file('../static/index.html')
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
