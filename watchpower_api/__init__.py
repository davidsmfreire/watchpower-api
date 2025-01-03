from datetime import date
import time
from typing import Any, Optional
import requests
import hashlib

from watchpower_api.models import DeviceIdentifier

__version__ = "0.3.0"


class WatchPowerAPI:
    _BASE_URL: str = "http://android.shinemonitor.com/public/"
    _SUFFIX_CONTEXT: str = "&i18n=pt_BR&lang=pt_BR&source=1&_app_client_=android&_app_id_=wifiapp.volfw.watchpower&_app_version_=1.0.6.3"
    _COMPANY_KEY: str = "bnrl_frRFjEz8Mkn"

    def __init__(self) -> None:
        # auth
        self.token: Optional[str] = None
        self.secret: Optional[str] = "ems_secret"
        self.expire: Optional[str] = None

    @staticmethod
    def _generate_salt() -> str:
        return str(round(time.time() * 1000))

    @staticmethod
    def _sha1_str_lower_case(byte_array: bytes) -> str:
        sha1_hash = hashlib.sha1(byte_array).hexdigest()  # nosec
        return sha1_hash.lower()

    def _hash(self, *args: str) -> str:
        arg_concat = ""
        for arg in args:
            arg_concat = arg_concat + arg
        return self._sha1_str_lower_case(bytes(arg_concat, encoding="utf-8"))

    def _ensure_logged_in(self) -> tuple[str, str]:
        if self.token is None or self.secret is None:
            raise RuntimeError(
                "Must login first using .login(username, password) method"
            )
        return self.token, self.secret

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
            f"&action=authSource&usr={username}&company-key={self._COMPANY_KEY}"
            + self._SUFFIX_CONTEXT
        )

        salt = self._generate_salt()

        password_hash = self._hash(password)

        sign = self._hash(salt, password_hash, base_action)

        url = self._BASE_URL + f"?sign={sign}&salt={salt}" + base_action

        response = requests.get(url, timeout=10)

        response_data: dict[str, Any] = response.json()

        if response.status_code == 200:
            error_code: int = response_data["err"]
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
        dev_code: int,
        dev_addr: int,
    ) -> dict[str, Any]:
        """Get inverter daily data

        Args:
            day (date): Day of data collection
            serial_number (str): Inverter serial number, can be found through the WatchPower android application or
            through the result of .get_devices(). Only numerical digits
            wifi_pn (str): Wifi PN, can be found through the WatchPower android application or through the result of
            .get_devices(). It looks like 'W{digits}'
            dev_code (int, optional): Device code. You can get it through .get_devices() result.
            dev_addr (int, optional): Device address. You can get it through .get_devices() result.

        Raises:
            RuntimeError: If there is an http error or the api returns a specific error

        Returns:
            dict: response json
        """
        token, secret = self._ensure_logged_in()
        _date = day.isoformat()
        base_action = (
            f"&action=queryDeviceDataOneDay&pn={wifi_pn}&devcode={dev_code}&sn={serial_number}&devaddr={dev_addr}&date={_date}"
            + self._SUFFIX_CONTEXT
        )
        salt = self._generate_salt()
        sign = self._hash(salt, secret, token, base_action)
        auth = f"?sign={sign}&salt={salt}&token={self.token}"
        url = self._BASE_URL + auth + base_action
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            response_data: dict[str, Any] = response.json()
            error_code: int = response_data["err"]
            if error_code == 0:
                return response_data
            raise RuntimeError(response_data)
        raise RuntimeError(response.status_code)

    def get_devices(
        self,
    ) -> list[DeviceIdentifier]:
        """Get user connected devices

        Raises:
            RuntimeError: If there is an http error or the api returns a specific error

        Returns:
            dict: response json
        """
        token, secret = self._ensure_logged_in()
        base_action = "&action=webQueryDeviceEs" + self._SUFFIX_CONTEXT
        salt = self._generate_salt()
        sign = self._hash(salt, secret, token, base_action)
        auth = f"?sign={sign}&salt={salt}&token={self.token}"
        url = self._BASE_URL + auth + base_action
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            response_data: dict[str, Any] = response.json()
            error_code: int = response_data["err"]
            if error_code == 0:
                return [
                    DeviceIdentifier(**data) for data in response_data["dat"]["device"]
                ]
            raise RuntimeError(response_data)
        raise RuntimeError(response.status_code)

    def get_device_daily_data(
        self,
        device_identifier: DeviceIdentifier,
        day: date,
    ) -> dict[str, Any]:
        """Get inverter daily data

        Args:
            day (date): Day of data collection
            device_identifier (DeviceIdentifier): Inverter identifier

        Raises:
            RuntimeError: If there is an http error or the api returns a specific error

        Returns:
            dict: response json
        """
        return self.get_daily_data(
            day=day,
            serial_number=device_identifier.serial_number,
            wifi_pn=device_identifier.wifi_pin,
            dev_code=device_identifier.device_code,
            dev_addr=device_identifier.device_address,
        )
