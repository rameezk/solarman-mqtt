import os

POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL"))
SOLARMAN_USERNAME = os.environ.get("SOLARMAN_USERNAME")
SOLARMAN_PASSWORD = os.environ.get("SOLARMAN_PASSWORD")
SOLARMAN_DEVICE_ID = os.environ.get("SOLARMAN_DEVICE_ID")
SOLARMAN_SITE_ID = os.environ.get("SOLARMAN_SITE_ID")
LOW_BATTERY_LEVEL = int(os.environ.get("LOW_BATTERY_LEVEL", 40))
MQTT_BROKER_HOST = os.environ.get("MQTT_BROKER_HOST")
MQTT_BROKER_PORT = int(os.environ.get("MQTT_BROKER_PORT", 1883))

assert None not in [
    POLL_INTERVAL,
    SOLARMAN_USERNAME,
    SOLARMAN_PASSWORD,
    SOLARMAN_DEVICE_ID,
    SOLARMAN_SITE_ID,
    LOW_BATTERY_LEVEL,
    MQTT_BROKER_HOST
], "Please provide a valid environment configuration"
