import requests
from typing import List, Any
from pydantic import BaseModel, Field
from enum import Enum
import hashlib


class SolarmanFieldName(Enum):
    BATTERY_POWER = "Battery Power"
    TOTAL_GRID_POWER = "Total Grid Power"
    SOC = "SoC"
    NOT_SPECIFIED = "Not Specified"

    @classmethod
    def _missing_(cls, value: object):
        return SolarmanFieldName.NOT_SPECIFIED


class SolarmanCategoryName(Enum):
    BATTERY = "Battery"
    POWER_GRID = "Power Grid"
    NOT_SPECIFIED = "Not Specified"

    @classmethod
    def _missing_(cls, value: object):
        return SolarmanCategoryName.NOT_SPECIFIED


class SolarmanField(BaseModel):
    key: SolarmanFieldName
    value: str
    unit: str = None


class SolarmanParamCategory(BaseModel):
    name: SolarmanCategoryName
    fields: List[SolarmanField] = Field(alias="fieldList")


class SolarmanDetail(BaseModel):
    param_category_list: List[SolarmanParamCategory] = Field(alias="paramCategoryList")


class State(BaseModel):
    grid_power: int  # watts
    battery_soc: int  # percentage
    battery_power: int  # watt


class SolarmanAPI:
    base_url = "https://home.solarmanpv.com"
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15"
    username: str
    password: str
    access_token: str = None
    refresh_token: str = None

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def login(self):
        print("Attempting to login to solarman")
        headers = {
            "User-Agent": self.user_agent,
        }
        data = {
            "grant_type": "password",
            "username": self.username,
            "clear_text_pwd": self.password,
            "password": hashlib.sha256(self.password.encode('utf-8')).hexdigest(),
            "identity_type": 2,
            "client_id": "test",
        }
        response = requests.post(
            f"{self.base_url}/oauth-s/oauth/token", data=data, headers=headers
        )
        if response.status_code == 200:
            print("logged in to solarman")
            response_json = response.json()
            self.access_token = response_json.get("access_token", "")
            self.refresh_token = response_json.get("refresh_token", "")

    def is_logged_in(self) -> bool:
        headers = {
            "User-Agent": self.user_agent,
            "Authorization": f"Bearer {self.access_token}",
        }
        response = requests.get(
            f"{self.base_url}/user-s/acc/org/login-user", headers=headers
        )
        return response.status_code == 200

    def get_state(self, device_id: str, site_id: str) -> State:
        if not self.is_logged_in():
            self.login()

        headers = {
            "User-Agent": self.user_agent,
            "Authorization": f"Bearer {self.access_token}",
        }
        data = {
            "deviceId": device_id,
            "language": "en",
            "needRealTimeDataFlag": True,
            "siteId": site_id,
        }
        response = requests.post(
            f"{self.base_url}/device-s/device/detail", headers=headers, json=data
        )

        if response.status_code == 200:
            response_json = response.json()
            solarman_detail = SolarmanDetail(**response_json)

            power_grid_category = [
                p
                for p in solarman_detail.param_category_list
                if p.name == SolarmanCategoryName.POWER_GRID
            ][0]
            total_grid_power_field = [
                f
                for f in power_grid_category.fields
                if f.key == SolarmanFieldName.TOTAL_GRID_POWER
            ][0]

            battery_category = [
                p
                for p in solarman_detail.param_category_list
                if p.name == SolarmanCategoryName.BATTERY
            ][0]
            battery_power_field = [
                f
                for f in battery_category.fields
                if f.key == SolarmanFieldName.BATTERY_POWER
            ][0]
            battery_soc_field = [
                f for f in battery_category.fields if f.key == SolarmanFieldName.SOC
            ][0]

            state = State(
                grid_power=total_grid_power_field.value,
                battery_power=battery_power_field.value,
                battery_soc=battery_soc_field.value,
            )
            return state

        else:
            print("Failed to retrieve state")
