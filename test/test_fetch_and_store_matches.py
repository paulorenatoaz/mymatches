import unittest
from unittest.mock import patch
import os
import json
import logging

from mymatches import setup_logging
from mymatches.fetch_and_store_matches import fetch_and_store_matches

# Constants
CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'test_config')
DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')




class TestFetchAndStoreMatches(unittest.TestCase):
    """
    Test the fetch_and_store_matches function.
    """

    @patch('mymatches.fetch_and_store_matches.CONFIG_DIR', CONFIG_DIR)
    @patch('mymatches.fetch_and_store_matches.DATA_DIR', DATA_DIR)
    def test_fetch_and_store_matches(self):
        """
        This test checks if the function creates matches data files for all teams in the config file.
        """


        # Get team ids from the test config file
        config_path = os.path.join(CONFIG_DIR, 'config.json')
        with open(config_path, 'r', encoding='utf-8') as config_file:
            config = json.load(config_file)
            team_ids = list(config['CALENDARS'].keys())

        matches_dir = os.path.join(DATA_DIR, 'matches')

        # Backup existing matches data files
        for team_id in team_ids:
            matches_file = os.path.join(matches_dir, f'matches{team_id}.json')
            if os.path.exists(matches_file):
                os.rename(matches_file, matches_file + '.bak')

        # Call the function to test
        fetch_and_store_matches()

        try:
            # Check if matches data files are created for all teams in the config file
            for team_id in team_ids:
                matches_file = os.path.join(matches_dir, f'matches{team_id}.json')
                self.assertTrue(os.path.exists(matches_file))
        except AssertionError as e:
            # Restore backup files if the test fails
            logging.error("Test failed: Matches data files were not created for all teams")
            for team_id in team_ids:
                matches_file = os.path.join(matches_dir, f'matches{team_id}.json')
                if os.path.exists(matches_file + '.bak'):
                    os.rename(matches_file + '.bak', matches_file)
            raise e
        else:
            # Delete backup files if the test passes
            for team_id in team_ids:
                matches_file = os.path.join(matches_dir, f'matches{team_id}.json.bak')
                if os.path.exists(matches_file):
                    os.remove(matches_file)
            logging.info("Test passed: Matches data files were successfully created for all teams")

if __name__ == '__main__':
    unittest.main()
