#!/usr/bin/env python3
import sys
import time
import RPi.GPIO as gpio

from ultrasound import UltraSound
from ultrahue import HueBridge, Light

us1 = UltraSound(trigger_pin=27, echo_pin=17)
us2 = UltraSound(trigger_pin=23, echo_pin=24)

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

if __name__ == '__main__':
    flur = [hue.get_light_by_name("F 1"), hue.get_light_by_name("F 2")]
    assert all(flur)

    print_lights(flur)
    switch_lights(flur, True)
    time.sleep(1)
    print_lights(flur)
    switch_lights(flur, False)
    print_lights(flur)

    #uss = [us2]

    gpio.cleanup()
    sys.exit(0)

