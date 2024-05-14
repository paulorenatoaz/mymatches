import os
from datetime import datetime, timedelta

def is_file_recent(file_path, days=1):
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
