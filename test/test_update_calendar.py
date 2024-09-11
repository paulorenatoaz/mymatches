import json
import logging
import unittest
from unittest.mock import patch
import os
from mymatches import setup_logging, update_calendars


# Constants
CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'test_config')
DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')


class TestUpdateCalendars(unittest.TestCase):
    """
    Test the update_calendars function.
    """
    @patch('mymatches.update_calendars.CONFIG_DIR', CONFIG_DIR)
    @patch('mymatches.update_calendars.DATA_DIR', DATA_DIR)
    def test_update_calendars(self):
        # create log file for update_calendars if it does not exist
        log_file = os.path.join(DATA_DIR, 'logs', 'update_calendars.log')
        if not os.path.exists(log_file):
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            open(log_file, 'w').close()
            initial_log_size = 0
        else:
            with open(log_file, 'r') as f:
                logs_content = f.read()
                initial_log_size = len(logs_content)

        # Run the update_calendars function
        update_calendars()

        # Check for error messages at each new added line in the update_calendars log file
        with open(log_file, 'r') as f:
            f.seek(initial_log_size)  # Move the pointer to the initial log size
            new_logs_content = f.read()

        # Assert that there are no error messages in the new log content
        try:
            self.assertNotIn("ERROR", new_logs_content, "The log file contains error messages.")
        except AssertionError as e:
            # Print the error message
            logging.error("Test failed: The log file contains error messages for the last execution.")
            raise e
        else:
            logging.info("Test passed: The log file does not contain error messages for the last execution.")

if __name__ == '__main__':
    unittest.main()
