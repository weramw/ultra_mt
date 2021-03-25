#!/usr/bin/env python3
import sys
import os
import time
import logging
import RPi.GPIO as gpio

from ultra_sound import UltraSound
from ultra_features import UltraSoundBuffer, UltraSoundFilter, UltraSoundFeatureWalkThrough, UltraSoundFeatureMotion, UltraSoundFeatureWalkThroughFiltered
from ultra_switch import UltraSwitch
from ultra_hue import HueBridge, Light

us_hall = UltraSound(trigger_pin=17, echo_pin=27)
us_bath = UltraSound(trigger_pin=23, echo_pin=24)

uf_hall = UltraSoundFilter(us_hall)
uf_bath = UltraSoundFilter(us_bath)
us_feature_hall_filtered = UltraSoundFeatureWalkThroughFiltered(uf_hall, 0.8, 0.2)
us_feature_bath_filtered = UltraSoundFeatureWalkThroughFiltered(uf_bath, 0.7, 0.2)

door_reed = UltraSwitch(switch_pin=25)

hue_ip = "192.168.0.87"
api_key = "tNmBJLQdGdYBta51nzwU2PP8GfzuzFFBlup5h9c2"
hue = HueBridge(hue_ip, api_key)

logger = None

def print_lights(ll):
    for l in ll:
        l.update()
        print(l)

def switch_lights(ll, on):
    for l in ll:
        l.switch(on)

def any_light_on(ll):
    for l in ll:
        l.update()
    return any([l.is_on() for l in ll])

def flash_lights(lights):
    switch_lights(lights, False)
    time.sleep(0.5)
    switch_lights(lights, True)
    time.sleep(0.5)
    switch_lights(lights, False)

class UltraMt(object):
    def __init__(self, lights):
        self.lights = lights
        self.last_light_trigger = None
        self.trigger_interval = None
        self.interval_active = False
        self.lights_were_on = False     # if the lights were one when the current interval was triggered

    def update(self):
        self.ultra_mt()
        if self.trigger_interval is not None:
            logger.debug(f"Light Interval active: {self.interval_active}, Interval: [{self.trigger_interval[0]:.2f}, {self.trigger_interval[1]:.2f}] - {self.trigger_interval[1] - self.trigger_interval[0]:.2f}s, Lights were on: {self.lights_were_on}")
        self.update_lights()

    def update_lights(self):
        if self.interval_active:
            switch_lights(self.lights, True)
            logger.info("Switching Lights on during active interval")
            return
        if self.trigger_interval is None:
            return

        # we have an inactive interval
        if self.lights_were_on:     # we didnt switch them on -> we dont switch them off
            self.trigger_interval = None
            return

        now = time.time()
        trigger_time = now - self.trigger_interval[1]
        logger.info(f"Time since last trigger: {trigger_time:.1f}s")
        if trigger_time > 15.0:
            switch_lights(self.lights, False)
            self.trigger_interval = None
            logger.info("Switching lights off after inactive interval")
    
    def ultra_mt(self):
        if self.sensor_triggered():
            now = time.time()
            if self.trigger_interval is None or not self.interval_active:   # new interval
                self.trigger_interval = (now, now)
                self.lights_were_on = any_light_on(self.lights)
            else:   # we have an active interval - just push the end
                self.trigger_interval = (self.trigger_interval[0], now)
            self.interval_active = True
        else:
            self.interval_active = False

    def sensor_triggered(self):
        logger.debug("Features: Hall   Bath")
        hall_motion = us_feature_hall_filtered.has_motion()
        bath_motion = us_feature_bath_filtered.has_motion()
        logger.debug(f"us_feature_hall: {hall_motion}")
        logger.debug(f"us_feature_bath: {bath_motion}")
        door_open = not door_reed.is_on()
        logger.debug(f"door_open: {door_open}")
        return hall_motion or bath_motion or door_open

def setupLogging():
    # TODO
    # enable/disable debug logging for console/files
    global logger
    log_path = "./"
    if os.geteuid() == 0:
        log_path = "/var/log/ultra-mt"

    logger = logging.getLogger("ultra_mt")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    if "log" in sys.argv[1:]:
        fh = logging.FileHandler(os.path.join(log_path, "ultra_mt.log"))
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    if "log_debug" in sys.argv[1:]:
        fhd = logging.FileHandler(os.path.join(log_path, "ultra_mt_debug.log"))
        fhd.setLevel(logging.DEBUG)
        fhd.setFormatter(formatter)
        logger.addHandler(fhd)

if __name__ == '__main__':
    setupLogging()

    flur = [hue.get_light_by_name("F 1"), hue.get_light_by_name("F 2")]
    print_lights(flur)
    assert all(flur)

    switch_lights(flur, False)

    flash_lights(flur)
    logger.info("Calibrating...")
    uf_hall.calibrate()
    uf_bath.calibrate()
    logger.info("Done.")
    flash_lights(flur)
    time.sleep(1.0)
    flash_lights(flur)

    ultra_mt = UltraMt(flur)

    try:
        while True:
            uf_hall.update()
            uf_bath.update()
            ultra_mt.update()
            time.sleep(0.1)
    except KeyboardInterrupt:
        gpio.cleanup()

    gpio.cleanup()
    sys.exit(0)

