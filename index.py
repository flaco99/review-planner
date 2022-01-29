from flask import Flask
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import traceback
import datetime

app = Flask(__name__)


@app.route('/')
def home():
    html = """
    <html>
    <head>
    <title>just a page</title>
    <script src="https://apis.google.com/js/platform.js" async defer></script>
    <meta name="google-signin-client_id" content="769017929605-rpovnc5j01547ktb1er5fc0qqcd6fcer.apps.googleusercontent.com">
    <script>
function onSignIn(googleUser) {
  var profile = googleUser.getBasicProfile();
  var id_token = googleUser.getAuthResponse().id_token;
  window.location.replace("https://review-planner.vercel.app/dumdum/" + id_token);
  console.log('ID token: ' + id_token);
  console.log('ID: ' + profile.getId()); // Do not send to your backend! Use an ID token instead.
  console.log('Name: ' + profile.getName());
  console.log('Image URL: ' + profile.getImageUrl());
  console.log('Email: ' + profile.getEmail()); // This is null if the 'email' scope is not present.
}    
    </script>
    </head>
    <body>
    <p>Hello, I'm in html</p>
    <div class="g-signin2" data-onsuccess="onSignIn"></div>
    </body>
    </html>
    """
    return html


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
