import os
import sys

# Add the 'src' directory to the sys.path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(src_path)

from mymatches import fetch_and_store_matches

if __name__ == '__main__':
    fetch_and_store_matches()
