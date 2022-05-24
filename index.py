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
from datetime import time
import uuid


def weekend_to_weekday(day: datetime.datetime) -> datetime.datetime:
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
    # newDay = newDay.strftime('%Y-%m-%d')
    # outDay = str(newDay) + day[10:]
    return newDay

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

@app.route('/about')
def about():

    if 'credentials' not in flask.session:
        return flask.redirect('authorize')
    credentials = Credentials(**flask.session['credentials'])
    calendar = build("calendar", "v3", credentials=credentials)

    return render_template('about.html')

@app.route('/apply_changes_to_single', methods = ['POST'])
def apply_changes_to_single():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')
    credentials = Credentials(**flask.session['credentials'])
    calendar = build("calendar", "v3", credentials=credentials)
    try:
        event = calendar.events().get(calendarId='votusm3rk7umll40ikri89ruu0@group.calendar.google.com',
                                            eventId='eventId').execute()

        eventname = request.form['eventname']
        desc = request.form['eventdescription']
        weekend_switch = 'weekendswitch' in request.form
        freq_range = request.form['freqrange']
        eventhour = request.form['eventhour']
        eventminute = request.form['eventminute']
        defaulteventtimeswitch = request.form.get('defaulteventtimeswitch')

        event['summary'] = eventname
        updated_event = calendar.events().update(calendarId='votusm3rk7umll40ikri89ruu0@group.calendar.google.com',
                                                     eventId=event['id'], body=event).execute()
        print(updated_event['updated'])
    except RefreshError:
        return flask.redirect('authorize')
    return flask.redirect(f'view_events?')

@app.route('/apply_changes_to_all', methods = ['POST'])
def apply_changes_to_all():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')
    credentials = Credentials(**flask.session['credentials'])
    calendar = build("calendar", "v3", credentials=credentials)
    try:
        eventID = request.form['eventId']
        chosenEvent = calendar.events().get(calendarId='votusm3rk7umll40ikri89ruu0@group.calendar.google.com', eventId=eventID).execute()
        print("AAAAAA")
        # print(eventID)
        print(chosenEvent['extendedProperties']['private']['tagID'])
        print("BBBBBB")
        eventTagID = chosenEvent['extendedProperties']['private']['tagID']

        eventList = calendar.events().list(calendarId='votusm3rk7umll40ikri89ruu0@group.calendar.google.com', maxResults=10,
                               privateExtendedProperty=f"tagID={eventTagID}").execute()

        eventname = request.form['eventname']
        desc = request.form['eventdescription']
        weekend_switch = 'weekendswitch' in request.form
        freq_range = request.form['freqrange']
        eventhour = request.form['eventhour']
        eventminute = request.form['eventminute']
        defaulteventtimeswitch = request.form.get('defaulteventtimeswitch')

        for event in eventList["items"]:
            print(f"AAAAAA   {event} BBBB")
            #event = calendar.events().get(calendarId='primary', eventId='eventId').execute()
            event['summary'] = eventname
            updated_event = calendar.events().update(calendarId='votusm3rk7umll40ikri89ruu0@group.calendar.google.com', eventId=event['id'], body=event).execute()
            print(updated_event['updated'])
    except RefreshError:
        return flask.redirect('authorize')
    return flask.redirect(f'view_events?event_tag_id={eventTagID}')

@app.route('/view_events', methods=['GET'])
def view_events():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    credentials = Credentials(**flask.session['credentials'])
    calendar = build("calendar", "v3", credentials=credentials)
    eventList = calendar.events().list(calendarId='votusm3rk7umll40ikri89ruu0@group.calendar.google.com', maxResults=10,
                                       privateExtendedProperty="appID=booboo").execute()
    print(eventList)
    event_links = [event.get('htmlLink') for event in eventList["items"]]
    event_ids = [event.get('id') for event in eventList["items"]]
    return render_template('success.html', all_links=event_links, event_ids=event_ids, eventname="poop")

@app.route('/edit', methods=['GET'])
def get_info_to_edit():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    credentials = Credentials(**flask.session['credentials'])
    calendar = build("calendar", "v3", credentials=credentials)

    eventId = request.args['event_id']
    event = calendar.events().get(calendarId='votusm3rk7umll40ikri89ruu0@group.calendar.google.com',
                                  eventId=eventId).execute()
    eventname = event['summary']
    print(event)
    return render_template('edit.html', event_name=eventname, event_id=eventId)

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
        eventhour = request.form['eventhour']
        eventminute = request.form['eventminute']
        defaulteventtimeswitch = request.form.get('defaulteventtimeswitch')
    except:
        import traceback
        traceback.print_exc()
        raise
    print(eventname, desc, weekend_switch, freq_range, eventhour, eventminute, defaulteventtimeswitch)
   # return render_template('success.html', eventname="foo", all_links=[])

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
        if weekend_switch:
            event_datetime = weekend_to_weekday(day0 + datetime.timedelta(days=rounddaysplus))

        # convert to pst timezone
        # pst_timezone = timezone('US/Pacific')
        # event_datetime = pst_timezone.localize(event_datetime)
        # event_datetime = event_datetime.astimezone(pst_timezone)

        # later, get the user's local defult timezone in their google calendar and convert it to their timezone.

        eventhour = int(eventhour)
        eventminute = int(eventminute)

        if defaulteventtimeswitch:
            ieventhour = eventhour
            ieventminute = eventminute
            # take this to index.html ?
            # next user creates new event, the initial time in the time picker will be ieventhour and ieventminute

        event_datetime = event_datetime.replace(hour = eventhour)
        event_datetime = event_datetime.replace(minute = eventminute)

        isoformat_datetime = event_datetime.isoformat()
        if weekend_switch:
            isoformat_datetime = weekend_to_weekday(event_datetime).isoformat()

        tagID = str(uuid.uuid4())

        event = {
            'summary': eventname,
            'start': {
                'dateTime': isoformat_datetime,
                'timeZone': 'US/Pacific',
            },
            'end': {
                'dateTime': isoformat_datetime,
                'timeZone': 'US/Pacific',
            },
            "extendedProperties": {
                    "private": {
                        "tagID": tagID,
                        "appID": "booboo"
                    }
            }
        }
        print(event)
        # Call the Calendar API
        event = calendar.events().insert(calendarId='votusm3rk7umll40ikri89ruu0@group.calendar.google.com', sendNotifications=True, body=event).execute()
        all_links.append(event.get('htmlLink'))

        # set to the next day
        daysplus = daysplus * intervalfactor
        rounddaysplus = round(daysplus)
        duration = duration / 2
    return flask.redirect('view_events')


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