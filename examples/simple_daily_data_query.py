from datetime import date

import os
from dotenv import load_dotenv
from watchpower_api import WatchPowerAPI

load_dotenv()

START = "2024-06-01"
END = "2024-06-02"
USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]
SERIAL_NUMBER = os.environ["SERIAL_NUMBER"]
WIFI_PN = os.environ["WIFI_PN"]
DEV_CODE = int(os.environ["DEV_CODE"])
DEV_ADDR = int(os.environ["DEV_ADDR"])


def main():
    api = WatchPowerAPI()
    api.login(USERNAME, PASSWORD)
    raw_data = api.get_daily_data(
        date(2024, 6, 1), SERIAL_NUMBER, WIFI_PN, DEV_CODE, DEV_ADDR
    )
    print(raw_data)


if __name__ == "__main__":
    main()
