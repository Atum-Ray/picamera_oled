#!/usr/bin/python3

# Script to send a poweroff command to the pi-top v2 hub. Typically this
# is launched by systemd responding to halt.target/poweroff.target, to
# ensure the hub shuts down after the raspberry pi

from ptcommon.i2c_device import I2CDevice

CTRL__UI_OLED_CTRL = 0x14

try:

    hub = I2CDevice("/dev/i2c-1", 0x10)
    hub.connect()

    hub.write_byte(CTRL__UI_OLED_CTRL, 3)

except Exception as e:

    print("Error shutting down the hub: " + str(e))

