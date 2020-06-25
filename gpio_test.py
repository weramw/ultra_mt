#!/usr/bin/env python3
import sys
import RPi.GPIO as gpio
import time

if __name__ == '__main__':
    gpio.setmode(gpio.BCM)

    pins = [17, 27]
    for pin in pins:
        gpio.setup(pin, gpio.IN)
        val = gpio.input(pin)
        print(f"Pin {pin} is {val}")

    set_pins = []
    if len(sys.argv) > 1:
        set_pins.append((int(sys.argv[1]), int(sys.argv[2])))
    for sp in set_pins:
        pins.remove(sp[0])
        gpio.setup(sp[0], gpio.OUT)
        gpio.output(sp[0], bool(sp[1]))
        print(f"Set pin {sp[0]} to {bool(sp[1])}")

    for pin in pins:
        gpio.setup(pin, gpio.IN)
        val = gpio.input(pin)
        print(f"Pin {pin} is {val}")

    #gpio.cleanup()
