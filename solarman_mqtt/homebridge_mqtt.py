import time
import json

from .environment import LOW_BATTERY_LEVEL

from paho.mqtt.client import Client
from enum import Enum


class Service(Enum):
    CONTACT_SENSOR = "ContactSensor"
    LIGHT_SENSOR = "LightSensor"
    BATTERY = "Battery"


class Characteristic(Enum):
    CURRENT_AMBIENT_LIGHT_LEVEL = "CurrentAmbientLightLevel"
    CONTACT_SENSOR_STATE = "ContactSensorState"
    BATTERY_LEVEL = "BatteryLevel"
    STATUS_LOW_BATTERY = "StatusLowBattery"
    CHARGING_STATE="ChargingState"


from .solarman import State


class HomebridgeMQTT:
    TOPIC_ADD_ACCESSORY = "homebridge/to/add"
    TOPIC_ADD_SERVICE = "homebridge/to/add/service"
    TOPIC_SET_VALUE = "homebridge/to/set"

    INVERTER_SUPPLY_NAME = "Inverter Supply"
    INVERTER_BATTERY_POWER_NAME = "Inverter Battery Power"
    INVERTER_BATTERY_SOC_NAME = "Inverter Battery SOC"

    client: Client = None

    def __init__(self, host: str, port: int = 1883):
        self.client = Client()
        self.client.connect(host, port, keepalive=60)
        self.client.loop_start()

        while not self.client.is_connected():
            print("Waiting for connection to mqtt broker")
            time.sleep(2)

        self._register_accessories()

    def register_accessory(self, name: str, service_name: str, service: Service):
        message = {"name": name, "service_name": service_name, "service": service.value}
        self.client.publish(self.TOPIC_ADD_ACCESSORY, json.dumps(message))

    def register_service(
        self, accessory_name: str, service_name: str, service: Service
    ):
        message = {
            "name": accessory_name,
            "service_name": service_name,
            "service": service.value,
        }
        self.client.publish(self.TOPIC_ADD_SERVICE, json.dumps(message))

    def _register_accessories(self):
        self.register_accessory(
            self.INVERTER_SUPPLY_NAME, self.INVERTER_SUPPLY_NAME, Service.CONTACT_SENSOR
        )
        self.register_accessory(
            self.INVERTER_BATTERY_POWER_NAME,
            self.INVERTER_BATTERY_POWER_NAME,
            Service.LIGHT_SENSOR,
        )
        self.register_service(
            self.INVERTER_SUPPLY_NAME, self.INVERTER_BATTERY_SOC_NAME, Service.BATTERY
        )
        self.register_service(
            self.INVERTER_BATTERY_POWER_NAME,
            self.INVERTER_BATTERY_SOC_NAME,
            Service.BATTERY,
        )

    def _publish_value(
        self,
        accessory_name: str,
        service_name: str,
        characteristic: Characteristic,
        value: int,
    ):
        message = {
            "name": accessory_name,
            "service_name": service_name,
            "characteristic": characteristic.value,
            "value": value,
        }
        self.client.publish(self.TOPIC_SET_VALUE, json.dumps(message))

    def publish_state(self, state: State):
        # battery power
        lux_level = max(0.0001, state.battery_power)
        self._publish_value(
            self.INVERTER_BATTERY_POWER_NAME,
            self.INVERTER_BATTERY_POWER_NAME,
            Characteristic.CURRENT_AMBIENT_LIGHT_LEVEL,
            lux_level,
        )

        # battery soc
        self._publish_value(
            self.INVERTER_BATTERY_POWER_NAME,
            self.INVERTER_BATTERY_SOC_NAME,
            Characteristic.BATTERY_LEVEL,
            state.battery_soc,
        )
        self._publish_value(
            self.INVERTER_SUPPLY_NAME,
            self.INVERTER_BATTERY_SOC_NAME,
            Characteristic.BATTERY_LEVEL,
            state.battery_soc,
        )
        is_low_battery = state.battery_soc <= LOW_BATTERY_LEVEL
        self._publish_value(
            self.INVERTER_SUPPLY_NAME,
            self.INVERTER_BATTERY_SOC_NAME,
            Characteristic.STATUS_LOW_BATTERY,
            int(is_low_battery),
        )
        self._publish_value(
            self.INVERTER_BATTERY_POWER_NAME,
            self.INVERTER_BATTERY_SOC_NAME,
            Characteristic.STATUS_LOW_BATTERY,
            int(is_low_battery),
        )

        # inverter/grid supply
        supply_from_inverter = False
        if state.battery_power > 0:
            supply_from_inverter = True
        self._publish_value(
            self.INVERTER_SUPPLY_NAME,
            self.INVERTER_SUPPLY_NAME,
            Characteristic.CONTACT_SENSOR_STATE,
            int(supply_from_inverter),
        )
        self._publish_value(
            self.INVERTER_SUPPLY_NAME,
            self.INVERTER_BATTERY_SOC_NAME,
            Characteristic.CHARGING_STATE,
            int(not(supply_from_inverter)),
        )
        self._publish_value(
            self.INVERTER_BATTERY_POWER_NAME,
            self.INVERTER_BATTERY_SOC_NAME,
            Characteristic.CHARGING_STATE,
            int(not(supply_from_inverter)),
        )
