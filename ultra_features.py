#!/usr/bin/env python3
import sys
import time
import math
import RPi.GPIO as gpio

from ultrasound import UltraSound

us_across = UltraSound(trigger_pin=17, echo_pin=27)
us_along = UltraSound(trigger_pin=23, echo_pin=24)

class UltraSoundFeatures(object):
    def __init__(self, us):
        self.ultra_sound = us

    def calibrate(self):
        """ Run initialization procedure on empty scene.

            Can block for a while."""
        raise NotImplementedError

    def update(self):
        """ Update the internal feature based on sensor data. """
        raise NotImplementedError

    def has_motion(self):
        """ Return if motion was detected. """
        raise NotImplementedError

class UltraSoundFeatureWalkThrough(UltraSoundFeatures):
    def __init__(self, us, min_detection_width=0):
        super().__init__(us)
        self.min_detection_width = min_detection_width
        self.empty_range = None
        self.empty_std = None
        self.last_distance = None
        self.calibration_time = 3.0
        self.distance_buffer = []       # (time, dist) pairs
        self.distance_buffer_max_age = 0.5 #1.0

    def calibrate(self):
        ranges = []
        start_time = time.time()
        while time.time() - start_time <= self.calibration_time:
            dist = self.ultra_sound.get_distance()
            time.sleep(0.05)
            if dist is not None:
                ranges.append(dist)
        if len(ranges) <= 1:
            raise RuntimeError("No valid ranges during calibration.")
            return
        self.empty_range = sum(ranges)/len(ranges)
        sqr_error = [(dist - self.empty_range)**2 for dist in ranges]
        self.empty_std = math.sqrt(sum(sqr_error)/(len(ranges) - 1))
        print(f"Calibrated empty range as {self.empty_range:.2f}m +- {self.empty_std:.3f}m")

    def update(self):
        """ Update the internal feature based on sensor data. """
        # TODO rolling buffer over X time and use max range in buffer
        now = time.time()
        cur_dist = self.ultra_sound.get_distance()
        if cur_dist is None:
            return
        #print(f"Update at {now}")
        self.last_distance = cur_dist
        self.distance_buffer.append((now, cur_dist))
        min_time = now - self.distance_buffer_max_age
        #print(f"mt {min_time}")
        #print(f"Start DB: size {len(self.distance_buffer)} [{self.distance_buffer[0][0]}, {self.distance_buffer[-1][0]}]")
        while self.distance_buffer and self.distance_buffer[0][0] < min_time:
            self.distance_buffer = self.distance_buffer[1:]
            #print(f"DB: size {len(self.distance_buffer)} [{self.distance_buffer[0][0]}, {self.distance_buffer[-1][0]}]")
        #print(f"Final DB: size {len(self.distance_buffer)} [{self.distance_buffer[0][0]}, {self.distance_buffer[-1][0]}]")

    def has_motion(self):
        """ Return if motion was detected. """
        if self.last_distance is None:
            return False
        if not self.distance_buffer:
            return False
        #print(self.distance_buffer)
        dists = [de[1] for de in self.distance_buffer]
        #print(dists)
        max_dist = max(dists)
        print(f"Distance: {max_dist:.2f}m < {self.empty_range - 3*self.empty_std - self.min_detection_width:.2f}m")
        return max_dist < self.empty_range - 3*self.empty_std - self.min_detection_width


if __name__ == '__main__':
    #uss = [us2]
    us_feature_across = UltraSoundFeatureWalkThrough(us_across, 0.2)
    print("Calibrating us_feature_across")
    us_feature_across.calibrate()

    try:
        while True:
            us_feature_across.update()
            print(f"us_feature_across: {us_feature_across.has_motion()}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        gpio.cleanup()

    sys.exit(0)

