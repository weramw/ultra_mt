#!/usr/bin/env python3
import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BCM)

class UltraSwitch(object):
    """
        Create a switch on switch_pin.

        if pull_up is not None, set the pull_up/down resistor.
    """
    def __init__(self, switch_pin, pull_up = True):
        self.switch_pin = switch_pin
        self.pull_up = pull_up
        if pull_up is not None:
            gpio.setup(self.switch_pin, gpio.IN, pull_up_down=gpio.PUD_UP if pull_up else gpio.PUD_DOWN)
        else:
            gpio.setup(self.switch_pin, gpio.IN)

    def is_on(self):
        """
            If self.pull_up is set, the switch is "on", when the state differs from its default pull up/down.
            Otherwise a switch is on, when it is high.
        """
        state = gpio.input(self.switch_pin)
        if state not in [gpio.LOW, gpio.HIGH]:
            return None
        if self.pull_up is None:
            return state == gpio.HIGH

        if self.pull_up:
            return state == gpio.LOW
        # pull_down
        return state == gpio.HIGH

if __name__ == '__main__':
    reed = UltraSwitch(switch_pin=25)

    try:
        while True:
            is_on = reed.is_on()
            print(f"Reed: {'on' if is_on else 'off'}") 
            time.sleep(0.1)
    # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        gpio.cleanup()

