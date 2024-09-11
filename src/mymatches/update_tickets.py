import os
import re
import time
from bs4 import BeautifulSoup
import requests
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import quote
from mymatches.utils import setup_logging
import platform
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# Constants
BLOG_URL = "https://vasco.com.br/noticias-home/"
SEARCH_TEXT = "ingresso"
WHATSAPP_SEND_URL = "https://web.whatsapp.com/send"

CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'config')
PHONE_NUMBER_LIST_PATH = os.path.join(CONFIG_DIR, 'phone_numbers.txt')

# get phone numbers from text file and put then into a list
with open(PHONE_NUMBER_LIST_PATH, 'r') as file:
    PHONE_NUMBERS_LIST = file.readlines()
    PHONE_NUMBERS_LIST = [number.strip() for number in PHONE_NUMBERS_LIST]


CHROME_DRIVER_PATH = r"path\to\chromedriver.exe"
CHROME_PROFILE_PATH = r"userfolder\AppData\Local\Google\Chrome\User Data"
PROFILE_DIRECTORY = "Profile x"  # Adjust this to the correct profile

LOGS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'logs')

# Setup logging configuration
LOG_FILE = os.path.join(LOGS_DIR, 'update_tickets.log')


def get_news_content(post_url):
    """
    Fetches and returns the content of the news article from the provided URL.

    Args:
        post_url (str): The URL of the news post.

    Returns:
        str: The content of the news post or an error message.
    """
    try:
        response = requests.get(post_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        content_element = soup.find('div', class_='mb-5')
        if content_element:
            content = content_element.get_text(separator="\n").strip()
            return content
        return "No content found."
    except Exception as e:
        logging.error(f"Error fetching news content: {e}")
        return "Error retrieving content."


def check_for_ticket_post(url, search_text):
    """
    Searches for a post that matches the search text and returns the post content.

    Args:
        url (str): The URL of the page to search.
        search_text (str): The text to search for in the post titles.

    Returns:
        str: The content of the matching post or None if no matching post is found.
    """
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        posts = soup.find_all('div', class_='box-noticias p-3 h-100 d-flex flex-column justify-content-between')

        for post in posts:
            title_element = post.find('h3')
            if title_element and search_text.lower() in title_element.text.lower():
                post_link = title_element.find_parent('a')['href']
                post_content = get_news_content(post_link)
                return post_content, post_link, title_element.text
        return None, None, None
    except Exception as e:
        logging.error(f"Error checking for post: {e}")
        return None, None, None


def send_whatsapp_message(phone_number, message, post_link):
    """
    Sends a WhatsApp message to a specified phone number using Selenium.

    Args:
        phone_number (str): The phone number to send the message to.
        message (str): The message to send.
        post_link (str): The link to the blog post.
    """
    encoded_message = quote(message)  # URL encode the message
    whatsapp_url = f"{WHATSAPP_SEND_URL}?phone={phone_number}&text={encoded_message}"

    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={CHROME_PROFILE_PATH}")
    chrome_options.add_argument(f"--profile-directory={PROFILE_DIRECTORY}")

    service = Service(executable_path=CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(whatsapp_url)

    # Wait for WhatsApp Web to load and send the message
    try:
        message_box = None
        for _ in range(20):  # Check for 100 seconds
            try:
                message_box = driver.find_element(By.CSS_SELECTOR, 'div[data-tab="6"]')
                if message_box:
                    break
            except:
                time.sleep(5)  # Wait 5 second and try again

        if message_box:
            send_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Send"]')
            send_button.click()
            logging.info(f'Message sent successfully for post: {post_link}')
        else:
            logging.error("Message input box not found.")
    except Exception as e:
        logging.error(f"Error occurred: {e}")
    finally:
        time.sleep(20)  # Wait before closing the browser
        driver.quit()


def create_event(event_summary, start_time, end_time, venue):
    """
    Creates an event object for Google Calendar.

    Args:
        event_summary (str): The summary of the event.
        start_time (datetime): The start time of the event.
        end_time (datetime): The end time of the event.
        venue (str): The location of the event.

    Returns:
        dict: The event object.

    """

    event = {
        'summary': event_summary,
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'UTC-3'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'UTC-3'},
        'location': venue,

        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 1440},  # 1 day before
                # {'method': 'popup', 'minutes': 1440},  # 1 day before
                {'method': 'email', 'minutes': 720},  # 12 hours before
                {'method': 'popup', 'minutes': 720},  # 12 hours before
                # {'method': 'popup', 'minutes': 360},  # 6 hours before
                {'method': 'popup', 'minutes': 180},  # 3 hours before
                # {'method': 'email', 'minutes': 120},  # 2 hour before
                # {'method': 'popup', 'minutes': 120},  # 2 hour before
                # {'method': 'email', 'minutes': 60},  # 1 hour before
                # {'method': 'popup', 'minutes': 60},  # 1 hour before
                # {'method': 'popup', 'minutes': 30},  # 30 minutes before
                # {'method': 'popup', 'minutes': 10},  # 10 minutes before
            ],
        },
    }

    return event


def add_or_update_event(calendar_id, service, event):
    """
    Adds or updates an event in the Google Calendar.

    Args:
        calendar_id (str): The calendar ID.
        service (googleapiclient.discovery.Resource): The Google Calendar service object.
        event (dict): The event details
    """

    try:
        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
        if created_event:
            logging.info(f"Successfully added event: {event['summary']}")
    except Exception as e:
        logging.error(f"Failed to add event: {event['summary']}.  Error: {str(e)}")


def kill_chrome_processes():
    """
    Kills all Chrome processes on the system.

    Raises:
        OSError: If the operating system is not supported.


    """
    system = platform.system()

    if system == "Windows":
        os.system("taskkill /f /im chrome.exe")  # For Windows
    elif system == "Linux" or system == "Darwin":  # Linux or MacOS
        os.system("pkill -f chrome")
    else:
        raise OSError("Unsupported operating system")


def extract_ticket_selling_info(post_content):
    """
    Extracts the ticket selling start date and time from the post content.

    Args:
        post_content (str): The content of the blog post.

    Returns:
        tuple: A tuple containing the extracted date and time, or None if not found.
    """
    # Regex pattern to find the date within parentheses followed by "a partir das" and the time

    pattern = r'\((\d{1,2}/\d{1,2})\).*a partir das *(\d{1,2}h)'

    post_content = post_content.replace('\n', '').replace('\r', '')
    match = re.search(pattern, post_content, re.IGNORECASE | re.DOTALL)

    if match:
        start_date = match.group(1)
        start_time = match.group(2)
        return start_date, start_time

    return None


def authenticate_google_oauth():
    """
    Authenticates the user using OAuth 2.0 and returns the Google Calendar service object.

    Returns:
        googleapiclient.discovery.Resource: The Google Calendar service object.

    """



    creds = None

    token_path = os.path.join(CONFIG_DIR, 'token.json')
    credentials_path = os.path.join(CONFIG_DIR, 'credentials.json')
    scopes =['https://www.googleapis.com/auth/calendar']

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, scopes)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)


def run_update_tickets():
    """
    Main function to check for a new post and send an update if a matching post is found.

    """
    post_content, post_link, post_title = check_for_ticket_post(BLOG_URL, SEARCH_TEXT)

    # check in log file if the post message is already sent
    setup_logging(LOG_FILE)

    if post_content:

        with open(LOG_FILE, 'r') as file:
            log_content = file.read()
            if post_link in log_content:
                logging.info(f"No new tickets post found")
                return

        message = f"New Tickets Post Auto Update Alert!\n\nContent:\n{post_content}\n\nPost Link: {post_link}"
        print(post_title)
        print(message)
        logging.info(f'Last post update: {post_link.split("/")[-2]}')

        # Extract the ticket selling information
        ticket_info = extract_ticket_selling_info(post_content)
        print(ticket_info)
        if ticket_info:
            start_date, start_time = ticket_info
            event_summary = post_title[19:]
            print(event_summary)
            # Combine the date and time into one string
            # Clean the time string by removing the comma and replacing 'h'
            start_time = start_time.replace(',', '').replace('h', ':00')

            # Split the time into hour and ensure it's zero-padded
            hour, minute = start_time.split(':')
            hour = hour.zfill(2)
            start_time = f'{hour}:{minute}'

            # Get the current year
            current_year = datetime.now().year

            # Parse the date string into day and month
            day, month = start_date.split('/')

            # Construct the ISO format string dynamically
            iso_format_str = f'{current_year}-{month.zfill(2)}-{day.zfill(2)}T{start_time}'

            # Parse the date and time string into a datetime object
            # Create the datetime object from the ISO format string
            start_time_obj = datetime.fromisoformat(iso_format_str)
            end_time = start_time_obj + timedelta(hours=48)

            venue = "sociogigante.com/ingressos"
            event = create_event(event_summary, start_time_obj, end_time, venue)
            # service_acc_key_path = os.path.join(CONFIG_DIR, 'service_account_key.json')
            # service = authenticate_google(service_acc_key_path)
            service = authenticate_google_oauth()
            calendar_id = "98e4f5e3788173b71456bc62c7e3ba201f03e2f330585e2be059a289ba078997@group.calendar.google.com"
            add_or_update_event(calendar_id, service, event)

        # WARNING! Whatsapp may ban numbers that uses automated messages. Do not use personal number to send messages, buy a new number for this service.
        #
        # for phone_number in PHONE_NUMBERS_LIST:
        #     kill_chrome_processes()
        #     send_whatsapp_message(phone_number, message, post_link)

    else:
        logging.info("No matching post found.")


if __name__ == "__main__":
    run_update_tickets()
