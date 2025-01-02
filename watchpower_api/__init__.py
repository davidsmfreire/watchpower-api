from datetime import date
import time
from typing import Any, Dict, List
import requests
import hashlib

from watchpower_api.models import DeviceIdentifiers


class WatchPowerAPI:
    base_url = "http://android.shinemonitor.com/public/"
    suffix_context = "&i18n=pt_BR&lang=pt_BR&source=1&_app_client_=android&_app_id_=wifiapp.volfw.watchpower&_app_version_=1.0.6.3"
    company_key = "bnrl_frRFjEz8Mkn"

    def __init__(self) -> None:
        # auth
        self.token = None
        self.secret = "ems_secret"
        self.expire = None

    @staticmethod
    def _generate_salt():
        return str(round(time.time() * 1000))

    @staticmethod
    def _sha1_str_lower_case(byte_array: bytes) -> str:
        sha1_hash = hashlib.sha1(byte_array).hexdigest()
        return sha1_hash.lower()

    def _hash(self, *args):
        arg_concat = ""
        for arg in args:
            arg_concat = arg_concat + arg
        return self._sha1_str_lower_case(bytes(arg_concat, encoding="utf-8"))

    def login(self, username: str, password: str) -> "WatchPowerAPI":
        """Authenticates against the API and stores relevant auth artifacts for follow-up requests using this instance

        Args:
            username (str): Username of the account you created in the WatchPower application
            password (str): Password of the account you created in the WatchPower application

        Raises:
            RuntimeError: If any API error occurs

        Returns:
            Self: same instance, with stored auth artifacts
        """
        base_action = (
            f"&action=authSource&usr={username}&company-key={self.company_key}"
            + self.suffix_context
        )

        salt = self._generate_salt()

        password_hash = self._hash(password)

        sign = self._hash(salt, password_hash, base_action)

        url = self.base_url + f"?sign={sign}&salt={salt}" + base_action

        response = requests.get(url)

        response_data = response.json()

        if response.status_code == 200:
            error_code = response_data["err"]
            if error_code == 0:
                print("Login successful!")
                self.secret = response_data["dat"]["secret"]
                self.token = response_data["dat"]["token"]
                self.expire = response_data["dat"]["expire"]
                return self
            raise RuntimeError(response_data)
        raise RuntimeError(response.status_code)

    def get_daily_data(
        self,
        day: date,
        serial_number: str,
        wifi_pn: str,
        dev_code: int = 2449,
        dev_addr: int = 1,
    ) -> Dict[str, Any]:
        """Get inverter daily data

        Args:
            day (date): Day of data collection
            serial_number (str): Inverter serial number, can be found through the WatchPower android application.
            Only numerical digits
            wifi_pn (str): Wifi PN, can be found through the WatchPower android application. It looks like 'W{digits}'
            dev_code (int, optional): Not sure what this is. Defaults to 2449.
            dev_addr (int, optional): Not sure what this is. Defaults to 1.

        Raises:
            RuntimeError: If there is an http error or the api returns a specific error

        Returns:
            dict: response json
        """
        _date = day.isoformat()
        base_action = (
            f"&action=queryDeviceDataOneDay&pn={wifi_pn}&devcode={dev_code}&sn={serial_number}&devaddr={dev_addr}&date={_date}"
            + self.suffix_context
        )
        salt = self._generate_salt()
        sign = self._hash(salt, self.secret, self.token, base_action)
        auth = f"?sign={sign}&salt={salt}&token={self.token}"
        url = self.base_url + auth + base_action
        response = requests.get(url)

        if response.status_code == 200:
            response_data = response.json()
            error_code = response_data["err"]
            if error_code == 0:
                return response_data
            raise RuntimeError(response_data)
        raise RuntimeError(response.status_code)

    def get_devices(
        self,
    ) -> List[DeviceIdentifiers]:
        """Get user connected devices

        Raises:
            RuntimeError: If there is an http error or the api returns a specific error

        Returns:
            dict: response json
        """
        base_action = "&action=webQueryDeviceEs" + self.suffix_context
        salt = self._generate_salt()
        sign = self._hash(salt, self.secret, self.token, base_action)
        auth = f"?sign={sign}&salt={salt}&token={self.token}"
        url = self.base_url + auth + base_action
        response = requests.get(url)

        if response.status_code == 200:
            response_data = response.json()
            error_code = response_data["err"]
            if error_code == 0:
                return [
                    DeviceIdentifiers(**data) for data in response_data["dat"]["device"]
                ]
            raise RuntimeError(response_data)
        raise RuntimeError(response.status_code)

    def get_device_daily_data(
        self,
        device_identifiers: DeviceIdentifiers,
        day: date,
    ) -> Dict[str, Any]:
        """Get inverter daily data

        Args:
            day (date): Day of data collection
            device_identifiers (DeviceIdentifiers): Inverter identifiers

        Raises:
            RuntimeError: If there is an http error or the api returns a specific error

        Returns:
            dict: response json
        """
        return self.get_daily_data(
            day=day,
            serial_number=device_identifiers.serial_number,
            wifi_pn=device_identifiers.wifi_pin,
            dev_code=device_identifiers.device_code,
            dev_addr=device_identifiers.device_address,
        )
