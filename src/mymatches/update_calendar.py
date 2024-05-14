# src/mymatches/update_calendar.py

import json
import os
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

"""
update_calendar.py

This script adds the upcoming matches for each team in the calendars.json file to the Google Calendar.

Functions:
authenticate_google: Authenticates the Google Calendar API using the service account file.
load_existing_events: Loads the existing events from the events file.
save_events: Saves the events to the events file.
add_or_update_event: Adds or updates an event in the Google Calendar.
add_matches_to_calendar: Adds the matches to the Google Calendar.

Constants:
CONFIG_FILE: The path to the config json file.
CALENDARS_FILE: The path to the calendars json file.

Usage:
Call the main function to add the upcoming matches for each team in the calendars.json file to the Google Calendar.

Example:
>>> main()


"""

# Constants
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '../../config/config.json')
CALENDARS_FILE = os.path.join(os.path.dirname(__file__), '../../data/calendars.json')



def authenticate_google(config):

	"""
	Authenticates the Google Calendar API using the service account file.

	Args:
		config (dict): The configuration dictionary.

	Returns:
		service (googleapiclient.discovery.Resource): The Google Calendar service object.

	Raise:
		ValueError: If the service account file is not found.

	"""

	service_account_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../', config['SERVICE_ACCOUNT_FILE']))

	if not os.path.exists(service_account_file):
		raise ValueError(f"The service account file {service_account_file} was not found, check SERVICE_ACCOUNT_FILE path in config/config.json.")

	credentials = Credentials.from_service_account_file(service_account_file, scopes=config['SCOPES'])
	return build('calendar', 'v3', credentials=credentials)


def load_existing_events(team_id):
	"""
	Loads the existing events from the events file.

	Args:
		team_id (str): The team ID.

	Returns:
		existing_events (dict): The existing events.

	Raise:
		TypeError: If team_id is not a string.

	"""

	if not isinstance(team_id, str):
		raise TypeError("team_id must be a string.")

	events_file = os.path.join(os.path.dirname(__file__), '../../data/events' + team_id + '.json')


	if os.path.exists(events_file):
		with open(events_file, 'r', encoding='utf-8') as f:
			return json.load(f)
	return {}


def save_events(team_id, events):
	events_file = os.path.join(os.path.dirname(__file__), '../../data/events' + team_id + '.json')
	with open(events_file, 'w', encoding='utf-8') as f:
		json.dump(events, f, ensure_ascii=False, indent=4)


def add_or_update_event(team_id, calendar_id, event_id, event, service):

	"""
	Adds or updates an event in the Google Calendar.

	Args:
		team_id (str): The team ID.
		calendar_id (str): The calendar ID.
		event_id (str): The event ID.
		event (dict): The event dictionary.
		service (googleapiclient.discovery.Resource): The Google Calendar service object.

	Returns:
		None

	Raise:
		TypeError: If team_id is not a string.
		TypeError: If calendar_id is not a string.
		TypeError: If event_id is not a string.
		TypeError: If event is not a dictionary.
		TypeError: If service is not a googleapiclient.discovery.Resource.



	"""

	if not isinstance(team_id, str):
		raise TypeError("team_id must be a string.")

	if not isinstance(calendar_id, str):
		raise TypeError("calendar_id must be a string.")

	if not isinstance(event_id, str):
		raise TypeError("event_id must be a string.")

	if not isinstance(event, dict):
		raise TypeError("event must be a dictionary.")

	existing_events = load_existing_events(team_id)

	if event_id in existing_events:
		service.events().update(calendarId=calendar_id, eventId=existing_events[event_id], body=event).execute()
		print(f"Updated event: {event['summary']}")
	else:
		created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
		existing_events[event_id] = created_event['id']
		save_events(team_id, existing_events)
		print(f"Added event: {event['summary']}")


def add_matches_to_calendar(team_id, calendar_id, service):
	"""
	Adds the matches to the Google Calendar.

	Args:
		team_id (str): The team ID.
		calendar_id (str): The calendar ID.
		service (googleapiclient.discovery.Resource): The Google Calendar service object.

	Returns:
		None

	Raise:
		TypeError: If team_id is not a string.
		TypeError: If calendar_id is not a string.

	"""

	if not isinstance(team_id, str):
		raise TypeError("team_id must be a string.")

	if not isinstance(calendar_id, str):
		raise TypeError("calendar_id must be a string.")


	json_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../', 'data', 'matches' + team_id + '.json'))
	with open(json_file_path, 'r', encoding='utf-8') as f:
		matches = json.load(f)

	for match in matches['campeonato-brasileiro']:

		if match['data_realizacao_iso']:
			start_time = datetime.fromisoformat(match['data_realizacao_iso'])
		else:
			continue
		end_time = start_time + timedelta(hours=2)
		event_summary = f"{match['time_mandante']['nome_popular']} vs {match['time_visitante']['nome_popular']}, {match['campeonato']['nome']}"
		event_id = match['partida_id']

		event = {
			'summary': event_summary,
			'start': {'dateTime': start_time.isoformat(), 'timeZone': 'America/Sao_Paulo'},
			'end': {'dateTime': end_time.isoformat(), 'timeZone': 'America/Sao_Paulo'},
			'location': match['estadio']['nome_popular'] if match['estadio'] else 'TBD'
		}

		add_or_update_event(team_id, calendar_id, str(event_id), event, service)


def main():

	"""
	Adds the upcoming matches for each team in the calendars.json file to the Google Calendar.

	Args:
		None

	Returns:
		None
	"""




	with open(CONFIG_FILE, 'r', encoding='utf-8') as config_file:
		config = json.load(config_file)

	with open(CALENDARS_FILE, 'r', encoding='utf-8') as calendars_data:
		calendars = json.load(calendars_data)

	service = authenticate_google(config)

	for team_id in calendars:
		calendar_id = calendars[team_id]
		add_matches_to_calendar(team_id, calendar_id, service)


if __name__ == '__main__':
	main()
