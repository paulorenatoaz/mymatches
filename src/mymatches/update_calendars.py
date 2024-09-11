import json
import os
import logging
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from mymatches import setup_logging

# Constants
CONFIG_DIR = os.path.join(os.path.dirname(__file__), '../../config')
DATA_DIR = os.path.join(os.path.dirname(__file__), '../../data')


def authenticate_google(key_path):
	"""
	Authenticates the Google Calendar API using the service account file path.

	Args:
		key_path (str): The path to the service account file.

	Returns:
		service (googleapiclient.discovery.Resource): The Google Calendar service object.
	"""
	credentials = Credentials.from_service_account_file(key_path, scopes=["https://www.googleapis.com/auth/calendar"])
	return build('calendar', 'v3', credentials=credentials)


def add_matches_to_calendar(team_id, calendar_id, service, data_dir):
	"""
	Adds the matches to the Google Calendar.

	Args:
		team_id (str): The team ID.
		calendar_id (str): The calendar ID.
		service (googleapiclient.discovery.Resource): The Google Calendar service object.
		data_dir (str): The path to the data directory.
	"""
	json_file_path = os.path.abspath(os.path.join(data_dir, 'matches', f'matches{team_id}.json'))

	with open(json_file_path, 'r', encoding='utf-8') as f:
		matches_data = json.load(f)

	# Iterate over the matches from the response
	for match in matches_data['response']:
		fixture = match['fixture']
		league = match['league']
		home_team = match['teams']['home']
		away_team = match['teams']['away']

		# Extract match details
		start_time = datetime.fromisoformat(fixture['date'])
		end_time = start_time + timedelta(hours=2)  # Assume match duration is 2 hours
		event_summary = f"{home_team['name']} vs {away_team['name']}, {league['name']}"
		event_id = str(fixture['id'])
		venue = fixture['venue']['name'] if fixture['venue'] else 'TBD'

		# Prepare the event
		event = {
			'summary': event_summary,
			'start': {'dateTime': start_time.isoformat(), 'timeZone': fixture['timezone']},
			'end': {'dateTime': end_time.isoformat(), 'timeZone': fixture['timezone']},
			'location': venue
		}

		# Add or update the event in the calendar
		add_or_update_event(team_id, calendar_id, event_id, event, service, data_dir)


def add_or_update_event(team_id, calendar_id, event_id, event, service, data_dir):
	"""
	Adds or updates an event in the Google Calendar.

	Args:
		team_id (str): The team ID.
		calendar_id (str): The calendar ID.
		event_id (str): The event ID.
		event (dict): The event details.
		service (googleapiclient.discovery.Resource): The Google Calendar service object.
		data_dir (str): The path to the data directory

	"""
	existing_events = load_existing_events(team_id, data_dir)

	if event_id in existing_events:
		try:
			updated_event = service.events().update(calendarId=calendar_id, eventId=existing_events[event_id],
			                                        body=event).execute()
			if updated_event:
				logging.info(f"Successfully updated event: {event['summary']}")
		except Exception as e:
			logging.error(f"Failed to update event: {event['summary']}. Event ID: {event_id}. Error: {str(e)}")
	else:
		try:
			created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
			existing_events[event_id] = created_event['id']
			save_events(team_id, existing_events, data_dir)
			if created_event:
				logging.info(f"Successfully added event: {event['summary']}")
		except Exception as e:
			logging.error(f"Failed to add event: {event['summary']}. Event ID: {event_id}. Error: {str(e)}")


def load_existing_events(team_id, data_dir):
	"""
	Loads the existing events from the events file.

	Args:
		team_id (str): The team ID.
		data_dir (str): The path to the data directory.

	Returns:
		dict: The existing events.
	"""
	events_file = os.path.join(data_dir, 'events', 'events' + team_id + '.json')

	if os.path.exists(events_file):
		with open(events_file, 'r', encoding='utf-8') as f:
			return json.load(f)
	return {}


def save_events(team_id, events, data_dir):
	"""
	Saves the events to the events file.

	Args:
		team_id (str): The team ID.
		events (dict): The events.
		data_dir (str): The path to the data directory.
	"""

	# create events folder if it does not exist
	events_dir = os.path.join(data_dir, 'events')
	if not os.path.exists(events_dir):
		os.makedirs(events_dir)

	events_file = os.path.join(data_dir, 'events', 'events' + team_id + '.json')
	with open(events_file, 'w', encoding='utf-8') as f:
		json.dump(events, f, ensure_ascii=False, indent=4)


def update_calendars():
	"""
	Updates the Google Calendars with the upcoming matches for each team.
	"""



	setup_logging(os.path.join(DATA_DIR, 'logs', 'update_calendars.log'))

	config_path = os.path.join(CONFIG_DIR, 'config.json')
	with open(config_path, 'r', encoding='utf-8') as config_file:
		config = json.load(config_file)

	service_acc_key_path = os.path.join(CONFIG_DIR, 'service_account_key.json')
	service = authenticate_google(service_acc_key_path)

	calendars = config['CALENDARS']

	for team_id in calendars:
		calendar_id = calendars[team_id]
		add_matches_to_calendar(team_id, calendar_id, service, DATA_DIR)



if __name__ == '__main__':
	update_calendars()
