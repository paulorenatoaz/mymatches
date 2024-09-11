import json
import os
import logging
from datetime import datetime, timedelta
import requests
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

"""
utils.py

This module contains utility functions used by the mymatches package.

Functions:

setup_logging: Setup logging configuration.
reset_calendar: Deletes all events from the Google Calendar.


"""


def setup_logging(log_path):
  """Setup logging configuration.

    Args:
        log_path (str): The path to the log file.

  """

  if not os.path.exists(os.path.dirname(log_path)):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

  logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
      logging.FileHandler(log_path),
      logging.StreamHandler()
    ]
  )

  # Suppress specific log messages
  logging.getLogger('oauth2client').setLevel(logging.ERROR)
  logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)


def reset_calendar(service, calendar_id):
  """
  Deletes all events from the Google Calendar.

  Args:
	  service (googleapiclient.discovery.Resource): The Google Calendar service object.
	  calendar_id (str): The calendar ID.
  """

  events = service.events().list(calendarId=calendar_id).execute()
  if 'items' in events:
    for event in events['items']:
      service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()
      logging.info(f"Successfully deleted event: {event['summary']}")

