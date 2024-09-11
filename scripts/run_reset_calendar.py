import os
import sys

# Add the 'src' directory to the sys.path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(src_path)

from mymatches import reset_calendar, authenticate_google

if __name__ == '__main__':

	CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'config')

	service_acc_key_path = os.path.join(CONFIG_DIR, 'service_account_key.json')
	service = authenticate_google(service_acc_key_path)

	calendar_id = "98e4f5e3788173b71456bc62c7e3ba201f03e2f330585e2be059a289ba078997@group.calendar.google.com"

	reset_calendar(service, calendar_id)
