import pandas as pd

import os
from tqdm import tqdm
from dotenv import load_dotenv
from watchpower_api import WatchPowerAPI

load_dotenv()
START = "2024-06-01"
END = "2024-06-02"
USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]
SERIAL_NUMBER = os.environ["SERIAL_NUMBER"]
WIFI_PN = os.environ["WIFI_PN"]
DEV_CODE = os.environ["DEV_CODE"]


def normalize_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    # Normalize the JSON data into a DataFrame
    df = pd.json_normalize(raw_data["dat"]["row"])
    titles = pd.json_normalize(raw_data["dat"]["title"])

    df[titles["title"]] = pd.DataFrame(df["field"].tolist(), index=df.index)
    df = df.drop(columns="field")
    return df


def main():
    api = WatchPowerAPI()
    api.login(USERNAME, PASSWORD)

    os.makedirs("outputs", exist_ok=True)
    all_data = []
    date_range = pd.date_range(START, END, freq="D")
    for _date in tqdm(date_range, total=len(date_range)):
        try:
            raw_data = api.get_daily_data(
                _date.date(), SERIAL_NUMBER, WIFI_PN, DEV_CODE
            )
            data = normalize_data(raw_data)
            data.to_csv(f"outputs/daily_data_{_date.date().isoformat()}.csv")
            all_data.append(normalize_data(raw_data))
        except Exception as e:
            print(f"Failed to get date {_date.date()}: {e}")
            continue

    all_data = pd.concat(all_data)
    all_data.to_csv("outputs/all_daily_data.csv")


if __name__ == "__main__":
    main()
