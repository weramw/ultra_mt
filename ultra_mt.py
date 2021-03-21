#!/usr/bin/env python3
import sys
import time
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

last_light_trigger = None

hue_ip = "192.168.0.87"
api_key = "tNmBJLQdGdYBta51nzwU2PP8GfzuzFFBlup5h9c2"
hue = HueBridge(hue_ip, api_key)

def print_lights(ll):
    for l in ll:
        l.update()
        print(l)

def switch_lights(ll, on):
    for l in ll:
        l.switch(on)

def flash_lights(lights):
    switch_lights(lights, False)
    time.sleep(0.5)
    switch_lights(lights, True)
    time.sleep(0.5)
    switch_lights(lights, False)

def update_lights(lights):
    global last_light_trigger
    if last_light_trigger is None:
        switch_lights(lights, False)
        return
    now = time.time()
    trigger_time = now - last_light_trigger
    print(f"Time since last trigger: {trigger_time:.1f}s")
    if trigger_time > 15.0:
        switch_lights(lights, False)

def ultra_mt(lights):
    global last_light_trigger
    print("Features: Hall   Bath")
    hall_motion = us_feature_hall_filtered.has_motion()
    bath_motion = us_feature_bath_filtered.has_motion()
    print(f"us_feature_hall: {hall_motion}")
    print(f"us_feature_bath: {bath_motion}")
    door_open = not door_reed.is_on()
    print(f"door_open: {door_open}")
    if hall_motion or bath_motion or door_open:
        last_light_trigger = time.time()
        switch_lights(lights, True)

if __name__ == '__main__':
    flur = [hue.get_light_by_name("F 1"), hue.get_light_by_name("F 2")]
    print_lights(flur)
    assert all(flur)

    switch_lights(flur, False)

    flash_lights(flur)
    print("Calibrating...")
    uf_hall.calibrate()
    uf_bath.calibrate()
    print("Done.")
    flash_lights(flur)
    time.sleep(1.0)
    flash_lights(flur)

    try:
        while True:
            uf_hall.update()
            uf_bath.update()
            ultra_mt(flur)
            update_lights(flur)
            time.sleep(0.1)
    except KeyboardInterrupt:
        gpio.cleanup()

    gpio.cleanup()
    sys.exit(0)

