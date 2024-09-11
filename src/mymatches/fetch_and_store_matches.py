import logging
import requests
import json
import os
from datetime import datetime, timedelta
from mymatches import setup_logging  # Keep setup_logging in utils.py

# Constants
CONFIG_DIR = os.path.join(os.path.dirname(__file__), '../../config')
DATA_DIR = os.path.join(os.path.dirname(__file__), '../../data')


def fetch_matches(team_id, api_key):
    """
    Fetches the upcoming matches for a given team using api-football from RapidAPI.

    Args:
        team_id (str): The team ID.
        api_key (str): The API key for authorization.

    Returns:
        dict: The matches data if the request is successful.

    Raises:
        Exception: If the request fails.
    """
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {"team": team_id, "next": "99"}  # Adjust the "next" value as needed

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"Failed to fetch matches for team {team_id}. "
            f"Status code: {response.status_code}. "
            f"Response content: {response.text}"
        )


def is_file_recent(file_path, days=0.9):
    """
    Check if the file was modified in the last n days.

    Args:
        file_path (str): The path to the file.
        days (int): The number of days to check.

    Returns:
        bool: True if the file was modified in the last n days, False otherwise.
    """
    if os.path.exists(file_path):
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        return datetime.now() - file_mod_time < timedelta(days=days)
    return False


def store_matches(matches, json_file_path):
    """
    Stores the matches data in a JSON file.

    Args:
        matches (dict): The matches data.
        json_file_path (str): Path to the JSON file where matches data will be stored.
    """

    # create mathces directory if it does not exist
    matches_dir = os.path.join(os.path.dirname(json_file_path))
    if not os.path.exists(matches_dir):
        os.makedirs(matches_dir)

    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(matches, f, ensure_ascii=False, indent=4)
    logging.info(f"Successfully stored matches to {json_file_path}")


def load_config(config_path):
    """
    Loads the configuration file.

    Args:
        config_path (str): Path to the configuration file.

    Returns:
        dict: The configuration dictionary.

    Raises:
        FileNotFoundError: If the config file is not found.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found in this path: {config_path}. "
                                "Place the json file containing your calendar ids in the config directory")
    with open(config_path, 'r', encoding='utf-8') as config_file:
        return json.load(config_file)


def fetch_and_store_matches():
    """
    Fetches the upcoming matches for each team in the config.json file and stores them in the data directory.
    """
    setup_logging(os.path.join(DATA_DIR, 'logs', 'fetch_and_store_matches.log'))

    # Load the config file
    config_path = os.path.join(CONFIG_DIR, 'config.json')
    config = load_config(config_path)

    # Load the calendars
    calendars = config['CALENDARS']

    # Fetch and store the matches for each team
    for team_id in calendars:
        # Check if the file has already been updated today
        json_file_path = os.path.abspath(os.path.join(DATA_DIR, 'matches', f'matches{team_id}.json'))
        if is_file_recent(json_file_path):
            logging.info(f"The file {json_file_path} has been updated today.")
            continue

        # Ensure the data directory exists
        os.makedirs(os.path.dirname(json_file_path), exist_ok=True)

        try:
            matches = fetch_matches(team_id, config['API_KEY'])
            store_matches(matches, json_file_path)
            logging.info(f"Successfully fetched and stored matches for team {team_id}")
        except Exception as e:
            logging.error(f"Error processing team {team_id}: {e}")


