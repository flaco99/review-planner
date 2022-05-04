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
import calendar
import datetime


def weekend_to_weekday(day: datetime.datetime) -> str:
    '''takes a day in google calendar form. checks if it is a weekend.
    if it is a sunday, it converts it to the previous day (friday).
    if it is a saturday, it converts it to the next day (monday).
    if it is the same day that the event was created,
    the function returns the day that the event was created.
    returns the day in google calendar form.'''
    # dayL = [int(Day[0:4]),int(Day[5:7]),int(Day[8:10])]
    # year = int(day[0:4])
    # month = int(day[5:7])
    # day = int(day[8:10])

    today = (datetime.datetime.today() - datetime.timedelta(days=1)).isoformat() + 'Z'  # 'Z' indicates UTC time
    weekdaynum = calendar.weekday(day.year, day.month, day.day)
    if weekdaynum < 5: # if its a weekday
        return day
    elif weekdaynum == 5: # if its a saturday
        if str(day) == today:
            return day
        newDay = day - datetime.timedelta(days=1)
    elif weekdaynum == 6: # if its a sunday
        if str(day) == today:
            return day
        newDay = day + datetime.timedelta(days=1)
    newDay.strftime('%Y-%m-%d')
    outDay = str(newDay) + day[10:]
    return outDay

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

    try:
        eventname = request.form['eventname']
        desc = request.form['eventdescription']
        weekend_switch = 'weekendswitch' in request.form
        freq_range = request.form['freqrange']
    except:
        import traceback
        traceback.print_exc()
        raise
    print(eventname, desc, weekend_switch, freq_range)
   # return render_template('success.html', eventname="foo", all_links=[])

    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time



    # set review events

    # set the first day
    day0 = datetime.datetime.today() - datetime.timedelta(days=1)

    maxdays = 360
    daysplus = 1
    rounddaysplus = 1
    intervalfactor = float(freq_range)
    duration = 10
    all_links = []
    while daysplus < maxdays:
        event_datetime = weekend_to_weekday(day0 + datetime.timedelta(days=rounddaysplus))
        isoformat_datetime = event_datetime.isoformat() + 'Z'
        # print(day)
        if weekend_switch:
            isoformat_datetime = weekend_to_weekday(event_datetime)
            # print(day)

        event = {
            'summary': eventname,
            'start': {
                'dateTime': isoformat_datetime,
            },
            'end': {
                'dateTime': isoformat_datetime,
            }
        }
        # Call the Calendar API
        event = calendar.events().insert(calendarId='votusm3rk7umll40ikri89ruu0@group.calendar.google.com', sendNotifications=True, body=event).execute()
        all_links.append(event.get('htmlLink'))

        # set to the next day
        daysplus = daysplus * intervalfactor
        rounddaysplus = round(daysplus)
        duration = duration / 2

    return render_template('success.html', eventname=eventname, all_links=all_links)


@app.route('/authorize')
def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=json.loads(environ["CLIENT_SECRET_JSON"]),
        scopes=['https://www.googleapis.com/auth/calendar.events'])
    flow.redirect_uri = flask.url_for('oauthcallback', _external=True)
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
        print(f"URL={flask.url_for('oauthcallback', _external=True)}")
        flow.redirect_uri = flask.url_for('oauthcallback', _external=True)

        print(f"URL2={flask.request.url}")
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