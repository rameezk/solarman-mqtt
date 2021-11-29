# solarman-mqtt
> Poll Solarman APIs and send periodic updates to a MQTT broker

# Disclaimer
- This has only been tested on a Sunsynk inverter with a Solarman WiFi data logger. 
- The docker images only targets the `linx/arm/v7` architecture (raspberry pi 3b)

# Prerequisites
- docker
- docker-compose
- homebridge
- [homebridge-mqtt plugin](https://github.com/cflurin/homebridge-mqtt)

# Limitations
- Power values (usually watts) are modelled as a light sensor in HomeKit (in Lux). HomeKit does not support any sensor capable of displaying watts.

# Features
- [ ] Display battery power as a light sensor
- [ ] Display "Inverter Supply" as a contact sensor (useful for checking if supply is from Inverter or Grid)
- [ ] Display battery SOC as a meta property on the contact sensor