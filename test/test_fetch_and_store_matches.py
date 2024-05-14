import unittest
from mymatches.fetch_and_store_matches import fetch_and_store_matches
from mymatches.utils import is_file_recent

class TestFetchAndStoreMatches(unittest.TestCase):
    def test_is_file_recent(self):
        self.assertFalse(is_file_recent('non_existent_file.json'))

    def test_fetch_and_store_matches(self):
        fetch_and_store_matches()
        self.assertTrue(is_file_recent('data/matches.json'))

if __name__ == '__main__':
    unittest.main()
