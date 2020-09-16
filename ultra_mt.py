#!/usr/bin/env python3
import sys
import time
import RPi.GPIO as gpio

from ultra_sound import UltraSound
from ultra_features import UltraSoundBuffer, UltraSoundFeatureWalkThrough, UltraSoundFeatureMotion
from ultra_hue import HueBridge, Light

us_across = UltraSound(trigger_pin=17, echo_pin=27)
us_along = UltraSound(trigger_pin=23, echo_pin=24)
ub_across = UltraSoundBuffer(us_across)
ub_along = UltraSoundBuffer(us_along)
us_feature_across = UltraSoundFeatureWalkThrough(ub_across, 0.10)
#us_feature_motion = UltraSoundFeatureMotion(ub_along, 2)
us_feature_across_bath = UltraSoundFeatureWalkThrough(ub_along, 0.10)

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
    print(trigger_time)
    if trigger_time > 15.0:
        switch_lights(lights, False)

def ultra_mt(lights):
    global last_light_trigger
    across_motion = us_feature_across.has_motion()
    across_motion_bath = us_feature_across_bath.has_motion()
    print(f"us_feature_across: {across_motion}")
    print(f"us_feature_across_bath: {across_motion_bath}")
    if across_motion or across_motion_bath:
        last_light_trigger = time.time()
        switch_lights(lights, True)

if __name__ == '__main__':
    flur = [hue.get_light_by_name("F 1"), hue.get_light_by_name("F 2")]
    print_lights(flur)
    assert all(flur)

    switch_lights(flur, False)

    flash_lights(flur)
    print("Calibrating...")
    ub_across.calibrate()
    ub_along.calibrate()
    print("Done.")
    flash_lights(flur)
    time.sleep(1.0)
    flash_lights(flur)

    try:
        while True:
            ub_across.update()
            ub_along.update()
            ultra_mt(flur)
            update_lights(flur)
            time.sleep(0.1)
    except KeyboardInterrupt:
        gpio.cleanup()

    gpio.cleanup()
    sys.exit(0)

