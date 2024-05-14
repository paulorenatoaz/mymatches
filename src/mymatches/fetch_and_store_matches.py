import requests
import json
import os
from mymatches.utils import is_file_recent

"""
fetch_and_store_matches.py

This script fetches the upcoming matches for each team in the calendars.json file and stores them in the data directory.

Functions:
fetch_and_store_matches: Fetches the upcoming matches for each team in the calendars.json file and stores them in the data directory.

Constants:
CONFIG_FILE: The path to the config json file.
CALENDARS_FILE: The path to the calendars json file.


Usage:
Call the fetch_and_store_matches function to fetch and store the upcoming matches for each team in the calendars.json file.
		
Example:
>>> fetch_and_store_matches()


"""


# Constants
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '../../config/config.json')
CALENDARS_FILE = os.path.join(os.path.dirname(__file__), '../../data/calendars.json')

def fetch_and_store_matches():

	"""
	Fetches the upcoming matches for each team in the calendars.json file and stores them in the data directory.

	Args:
		None

	Returns:
		None

	"""


	with open(CONFIG_FILE, 'r', encoding='utf-8') as config_file:
		config = json.load(config_file)

	with open(CALENDARS_FILE, 'r', encoding='utf-8') as calendars_data:
		calendars = json.load(calendars_data)

	for team_id in calendars:

		json_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../', 'data', 'matches' + team_id + '.json' ))

		if is_file_recent(json_file_path):
			print(f"The file {json_file_path} has been updated today.")
			continue

		# Ensure the data directory exists
		os.makedirs(os.path.dirname(json_file_path), exist_ok=True)

		url = f"{config['API_FUTEBOL_BASE_URL']}/times/{team_id}/partidas/proximas"
		headers = {"Authorization": f"Bearer {config['API_KEY']}"}
		response = requests.get(url, headers=headers)

		if response.status_code == 200:
			matches = response.json()
			with open(json_file_path, 'w', encoding='utf-8') as f:
				json.dump(matches, f, ensure_ascii=False, indent=4)
			print(f"Matches stored in {json_file_path}")
		else:
			print(f"Error fetching matches: {response.status_code}")


if __name__ == '__main__':
	fetch_and_store_matches()
