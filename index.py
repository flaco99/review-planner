import sys
from flask import Flask
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import traceback
import google_auth_oauthlib.flow
from os import environ
import flask
from flask import render_template, request
import json
import calendar
import datetime
import uuid
import pytz
import logging

CAL_ID = 'primary'

def weekend_to_weekday(day: datetime.datetime) -> datetime.datetime:
    '''takes a day in google calendar form. checks if it is a weekend.
    if it is a sunday, it converts it to the previous day (friday).
    if it is a saturday, it converts it to the next day (monday).
    if it is the same day that the event was created,
    the function returns the day that the event was created.
    returns the day in google calendar form.'''

    today = (datetime.datetime.today() - datetime.timedelta(days=1)).isoformat()
    weekdaynum = calendar.weekday(day.year, day.month, day.day)

    if weekdaynum < 5: # if its a weekday
        return day
    if weekdaynum == 5: # if its a saturday
        if str(day) == today:
            return day
        newDay = day - datetime.timedelta(days=1)
    if weekdaynum == 6: # if its a sunday
        if str(day) == today:
            return day
        newDay = day + datetime.timedelta(days=1)
    return newDay

app = Flask(__name__,
            static_url_path='',
            static_folder='static/')
app.secret_key = environ["FLASK_SECRET_KEY"]

app.logger.addHandler(logging.StreamHandler(sys.stderr))

def verify_auth():
    if 'credentials' not in flask.session:
        raise RefreshError("no 'credentials' in session")
    credentials = Credentials(**flask.session['credentials'])
    calendar = build("calendar", "v3", credentials=credentials)
    calendar.events().list(calendarId='primary', maxResults=10).execute()
    # verify we can use the settings API
    calendar.settings().get(setting='timezone').execute()

@app.route('/')
def home():
    try:
        verify_auth()
    except RefreshError:
        return flask.redirect('authorize')
    return render_template('index.html')

@app.route('/about')
def about():
    try:
        verify_auth()
    except RefreshError:
        return flask.redirect('authorize')
    return render_template('about.html')

@app.route('/privacypolicy')
def privacypolicy():
    try:
        verify_auth()
    except RefreshError:
        return flask.redirect('authorize')
    return render_template('privacypolicy.html')

@app.route('/apply_changes_to_single', methods = ['POST'])
def apply_changes_to_single():
    try:
        verify_auth()
    except RefreshError:
        return flask.redirect('authorize')
    credentials = Credentials(**flask.session['credentials'])
    calendar = build("calendar", "v3", credentials=credentials)
    timeZone = calendar.settings().get(setting="timezone").execute()
    eventID = request.form['eventId']
    event = calendar.events().get(calendarId=CAL_ID,
                                  eventId=eventID).execute()
    eventname = request.form['eventname']
    desc = request.form['eventdescription']
    eventhour = request.form['eventhour']
    eventminute = request.form['eventminute']

    event['summary'] = eventname
    event['description'] = desc
    if len(eventhour) == 1:
        eventhour = '0' + eventhour
    if len(eventminute) == 1:
        eventminute = '0' + eventminute
    new_datetime = event['start']['dateTime'][:11] + eventhour + ':' + eventminute + event['start']['dateTime'][16:]
    event['start']['dateTime'] = new_datetime
    event['start']['timeZone'] = timeZone['value']
    event['end']['dateTime'] = new_datetime
    event['end']['timeZone'] = timeZone['value']
    updated_event = calendar.events().update(calendarId=CAL_ID,
                                             eventId=event['id'], body=event).execute()
    # print(updated_event['updated'])
    return flask.redirect(f'view_events?')

@app.route('/apply_changes_to_all', methods = ['POST'])
def apply_changes_to_all():
    try:
        verify_auth()
    except RefreshError:
        return flask.redirect('authorize')
    credentials = Credentials(**flask.session['credentials'])
    calendar = build("calendar", "v3", credentials=credentials)
    timeZone = calendar.settings().get(setting="timezone").execute()
    eventID = request.form['eventId']
    chosenEvent = calendar.events().get(calendarId=CAL_ID,
                                        eventId=eventID).execute()
    eventTagID = chosenEvent['extendedProperties']['private']['tagID']
    eventList = calendar.events().list(calendarId=CAL_ID, maxResults=10,
                                       privateExtendedProperty=f"tagID={eventTagID}").execute()
    eventname = request.form['eventname']
    desc = request.form['eventdescription']
    eventhour = request.form['eventhour']
    eventminute = request.form['eventminute']

    for event in eventList["items"]:
        event['summary'] = eventname
        event['description'] = desc
        if len(eventhour) == 1:
            eventhour = '0' + eventhour
        if len(eventminute) == 1:
            eventminute = '0' + eventminute
        # TODO get a better way to convert datetime
        new_datetime = event['start']['dateTime'][:11] + eventhour + ':' + eventminute + event['start']['dateTime'][16:]
        event['start']['dateTime'] = new_datetime
        event['start']['timeZone'] = timeZone['value']
        event['end']['dateTime'] = new_datetime
        event['end']['timeZone'] = timeZone['value']

        # TODO verify what update() expects
        updated_event = calendar.events().update(calendarId=CAL_ID,
                                                 eventId=event['id'], body=event).execute()
    return flask.redirect(f'view_events?event_tag_id={eventTagID}')

@app.route('/view_events', methods=['GET'])
def view_events():
    try:
        verify_auth()
    except RefreshError:
        return flask.redirect('authorize')

    credentials = Credentials(**flask.session['credentials'])
    calendar = build("calendar", "v3", credentials=credentials)
    minday = (datetime.datetime.today() - datetime.timedelta(days=1)).astimezone(datetime.timezone.utc)
    maxday = (datetime.datetime.today()).astimezone(datetime.timezone.utc)
    eventList = calendar.events().list(calendarId=CAL_ID,
                                       timeMax=maxday.isoformat(),
                                       timeMin=minday.isoformat(),
                                       privateExtendedProperty="appID=booboo").execute()
    event_links = [event.get('htmlLink') for event in eventList["items"]]
    event_ids = [event.get('id') for event in eventList["items"]]
    event_names = [event.get('summary') for event in eventList["items"]]
    event_descriptions = [event.get('description') for event in eventList["items"]]
    event_list = []
    for i in range(len(event_ids)):
        e = []
        e.append(event_ids[i])
        e.append(event_names[i])
        e.append(event_descriptions[i])
        e.append(event_links[i])
        event_list.append(e)
    return render_template('success.html', event_list=event_list, num_events=len(event_list))

@app.route('/edit', methods=['GET'])
def get_info_to_edit():
    try:
        verify_auth()
    except RefreshError:
        return flask.redirect('authorize')

    credentials = Credentials(**flask.session['credentials'])
    calendar = build("calendar", "v3", credentials=credentials)
    eventId = request.args['event_id']
    event = calendar.events().get(calendarId=CAL_ID,
                                  eventId=eventId).execute()
    # TODO what if the summary/description/etc is blank (None) ? in html, if user doesn't fill it out make it automatically "Untitled1" or smth
    datetime_str = event['start']['dateTime']
    # TODO make it match the user's timezone
    if datetime_str[11] == '0':
        hour = datetime_str[12]
    else:
        hour = datetime_str[11] + datetime_str[12]
    if datetime_str[14] == '0':
        minute = datetime_str[15]
    else:
        minute = datetime_str[14] + datetime_str[15]
    event_dict = {'id': eventId,
                  'name': event['summary'],
                  'description': event['description'],
                  'hour': hour,
                  'minute': minute}
    return render_template('edit.html', event_dict=event_dict)

@app.route('/create', methods = ['POST'])
def create():
    app.logger.info("create called")
    try:
        verify_auth()
    except RefreshError:
        return flask.redirect('authorize')

    credentials = Credentials(**flask.session['credentials'])
    calendar = build("calendar", "v3", credentials=credentials)
    timeZone = calendar.settings().get(setting="timezone").execute()

    eventname = request.form['eventname']
    desc = request.form['eventdescription']
    weekend_switch = 'weekendswitch' in request.form
    freq_range = request.form['freqrange']
    eventhour = request.form['eventhour']
    eventminute = request.form['eventminute']

    # set the first day
    day0 = datetime.datetime.today() - datetime.timedelta(days=1)
    tz = pytz.timezone(timeZone["value"])
    event_datetime = day0.astimezone(tz)

    tagID = str(uuid.uuid4())

    maxdays = 360
    daysplus = 1
    rounddaysplus = 1
    intervalfactor = float(freq_range)
    all_links = []
    while daysplus < maxdays:
        if weekend_switch:
            event_datetime = weekend_to_weekday(day0 + datetime.timedelta(days=rounddaysplus))
        eventhour = int(eventhour)
        eventminute = int(eventminute)
        event_datetime = event_datetime.replace(hour=eventhour)
        event_datetime = event_datetime.replace(minute=eventminute)
        isoformat_datetime = (day0 + datetime.timedelta(days=rounddaysplus)).isoformat()
        if weekend_switch:
            isoformat_datetime = weekend_to_weekday(event_datetime).isoformat()
        event = {
            'summary': eventname,
            'description': desc,
            'start': {
                'dateTime': isoformat_datetime,
                'timeZone': timeZone['value'],
            },
            'end': {
                'dateTime': isoformat_datetime,
                'timeZone': timeZone['value'],
            },
            "extendedProperties": {
                    "private": {
                        "tagID": tagID,
                        "appID": "booboo"
                    }
            }
        }
        # Call the Calendar API
        event = calendar.events().insert(calendarId=CAL_ID, sendNotifications=True, body=event).execute()
        all_links.append(event.get('htmlLink'))

        # set to the next day
        daysplus = daysplus * intervalfactor
        rounddaysplus = round(daysplus)
    return flask.redirect('view_events')

@app.route('/authorize')
def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=json.loads(environ["CLIENT_SECRET_JSON"]),
        scopes=['https://www.googleapis.com/auth/calendar.events', 'https://www.googleapis.com/auth/calendar.settings.readonly'])
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
            scopes=['https://www.googleapis.com/auth/calendar.events', 'https://www.googleapis.com/auth/calendar.settings.readonly'],
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