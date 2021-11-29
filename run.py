import time

import solarman_mqtt.environment as environment
from solarman_mqtt.solarman import SolarmanAPI, State
from solarman_mqtt.homebridge_mqtt import HomebridgeMQTT

if __name__ == "__main__":
    print("Booting")
    print(f"Will poll every {environment.POLL_INTERVAL} seconds")
    solarman_api = SolarmanAPI(
        environment.SOLARMAN_USERNAME, environment.SOLARMAN_PASSWORD
    )
    homebridge_mqtt = HomebridgeMQTT(environment.MQTT_BROKER_HOST, port=environment.MQTT_BROKER_PORT)
    while True:
        state: State = solarman_api.get_state(
            device_id=environment.SOLARMAN_DEVICE_ID,
            site_id=environment.SOLARMAN_SITE_ID,
        )
        print(f"{state=}")
        homebridge_mqtt.publish_state(state)
        time.sleep(environment.POLL_INTERVAL)
