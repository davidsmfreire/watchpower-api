import os

from dotenv import load_dotenv
from watchpower_api import WatchPowerAPI

load_dotenv()
USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]


def main():
    api = WatchPowerAPI()
    api.login(USERNAME, PASSWORD)
    devices = api.get_devices()

    for device in devices:
        print(device)


if __name__ == "__main__":
    main()
