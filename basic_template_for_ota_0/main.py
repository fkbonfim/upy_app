import sys
sys.path.append('/app')

import uasyncio as asyncio

import ubinascii
import machine, _thread


from mbus import MbusManager
# log = logging.getLogger("MBUS")
# log.setLevel(logging.DEBUG)

from wifi_mod import WiFiActivate
from ftpse_mod import FTPServerActivate

from heartbeat_mod import HeartbeatActivate

import logging
log = logging.getLogger("FTPSE")
log.setLevel(logging.INFO)

# import logging
# log = logging.getLogger("WIFI")
# log.setLevel(logging.DEBUG)


# def print_mbus(key, msg):
#     print("MAIN: {} - {}".format(key, msg))


def main():

    board_id = ubinascii.hexlify(machine.unique_id())
    board_name = "ESP32-{}".format(board_id.decode())
    print(board_name)
    
    mbus = MbusManager()
    mbus.start()

    # mbus.sub("MAIN", {"type": "ALL", "func": print_mbus})

    # Core
    WiFiActivate(mbus)

    FTPServerActivate(mbus)

    from telnetse_mod import TelnetServerActivate
    TelnetServerActivate(mbus)

    HeartbeatActivate(mbus)

    # App mod
    try:
        from relay_control_mod import RelayControlActivate
        RelayControlActivate(mbus)
    except Exception as e:
        print("REL exception .. {}".format(e))

    try:
        from button_control_mod import ButtonControlActivate
        ButtonControlActivate(mbus)
    except Exception as e:
        print("BTN exception .. {}".format(e))

    try:
        from mqttse_mod import MQTTClientActivate
        MQTTClientActivate(mbus, board_name)
    except Exception as e:
        print("MQTT exception .. {}".format(e))

    try:
        from pump_mod import PumpControlActivate
        PumpControlActivate(mbus)
    except Exception as e:
        print("PUMP exception .. {}".format(e))

    try:
        from light_mod import LightControlActivate
        LightControlActivate(mbus)
    except Exception as e:
        print("LIGHT exception .. {}".format(e))

    from machine import Pin, I2C

    sclPin = Pin(22)
    sdaPin = Pin(23)

    i2c = I2C(scl=sclPin, sda=sdaPin)

    try:
        from sensor_mod import SI7021ControlActivate
        SI7021ControlActivate(mbus, i2c)
    except Exception as e:
        print("SI7021 exception .. {}".format(e))

    try:
        from sensor_mod import BMP180ControlActivate
        BMP180ControlActivate(mbus, i2c)
    except Exception as e:
        print("BMP180 exception .. {}".format(e))

    loop = asyncio.get_event_loop()

    loop.create_task(run_wdt)

    _ = _thread.stack_size(8 * 1024)
    _thread.start_new_thread(loop.run_forever, ())


async def run_wdt():
    wdt = machine.WDT(timout_ms=20000)
    while True:
        wdt.feed()
        await asyncio.sleep(10)


if __name__ == '__main__':

    print("MAIN")
    main()
