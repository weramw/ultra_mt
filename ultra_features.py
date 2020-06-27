#!/usr/bin/env python3
import sys
import time
import math
import RPi.GPIO as gpio

from ultrasound import UltraSound

us_across = UltraSound(trigger_pin=17, echo_pin=27)
us_along = UltraSound(trigger_pin=23, echo_pin=24)

class UltraSoundBuffer(object):
    def __init__(self, us, distance_buffer_max_age=0.5):
        self.ultra_sound = us

        self.distance_buffer = []
        self.distance_buffer_max_age = distance_buffer_max_age

        self.calibration_time = 3.0
        self.calibration_range = None
        self.calibration_std = None

    def calibrate(self):
        """ Run initialization procedure on empty scene.
            Determine mean and std of dists within calibration_time.

            Can block for a while."""
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
        self.calibration_range = sum(ranges)/len(ranges)
        sqr_error = [(dist - self.calibration_range)**2 for dist in ranges]
        self.calibration_std = math.sqrt(sum(sqr_error)/(len(ranges) - 1))
        print(f"Calibrated range as {self.calibration_range:.2f}m +- {self.calibration_std:.3f}m")

    def update(self):
        """ Update the internal feature based on sensor data. """
        now = time.time()
        cur_dist = self.ultra_sound.get_distance()
        if cur_dist is None:
            return
        #print(f"Update at {now}")
        self.distance_buffer.append((now, cur_dist))
        min_time = now - self.distance_buffer_max_age
        #print(f"mt {min_time}")
        #print(f"Start DB: size {len(self.distance_buffer)} [{self.distance_buffer[0][0]}, {self.distance_buffer[-1][0]}]")
        while self.distance_buffer and self.distance_buffer[0][0] < min_time:
            self.distance_buffer = self.distance_buffer[1:]
            #print(f"DB: size {len(self.distance_buffer)} [{self.distance_buffer[0][0]}, {self.distance_buffer[-1][0]}]")
        #print(f"Final DB: size {len(self.distance_buffer)} [{self.distance_buffer[0][0]}, {self.distance_buffer[-1][0]}]")

    def get_distances(self, max_dist_age=None):
        if not self.distance_buffer:
            return None
        dists = [de[1] for de in self.distance_buffer]
        return dists

class UltraSoundFeatures(object):
    def __init__(self, ub):
        self.ultra_sound_buffer = ub

    def has_motion(self):
        """ Return if motion was detected. """
        raise NotImplementedError

class UltraSoundFeatureWalkThrough(UltraSoundFeatures):
    def __init__(self, ub, min_detection_width=0):
        super().__init__(ub)
        self.min_detection_width = min_detection_width

    def has_motion(self):
        """ Return if motion was detected. """
        dists = self.ultra_sound_buffer.get_distances()
        if not dists:
            return False
        max_dist = max(dists)
        print(f"Distance: {max_dist:.2f}m < {self.ultra_sound_buffer.calibration_range - self.ultra_sound_buffer.calibration_std - self.min_detection_width:.2f}m")
        return max_dist < self.ultra_sound_buffer.calibration_range - self.ultra_sound_buffer.calibration_std - self.min_detection_width

class UltraSoundFeatureMotion(UltraSoundFeatures):
    def __init__(self, ub, min_motion_mahanobilis):
        super().__init__(ub)
        self.min_motion_mahanobilis = min_motion_mahanobilis

    def has_motion(self):
        """ Return if motion was detected. """
        dists = self.ultra_sound_buffer.get_distances()
        if not dists or len(dists) < 2:
            return False
        mean_dist = sum(dists)/len(dists)
        sqr_error = [(dist - mean_dist)**2 for dist in dists]
        std_dist = math.sqrt(sum(sqr_error)/(len(dists) - 1))
        print(f"Motion: std {std_dist:.3f}m > min_motion_mahab {self.min_motion_mahanobilis} * calib std {self.ultra_sound_buffer.calibration_std} = {self.min_motion_mahanobilis * self.ultra_sound_buffer.calibration_std:.3f}")
        return std_dist > self.min_motion_mahanobilis * self.ultra_sound_buffer.calibration_std


if __name__ == '__main__':
    ub_across = UltraSoundBuffer(us_across)
    ub_along = UltraSoundBuffer(us_along)
    print("Calibrating...")
    ub_across.calibrate()
    ub_along.calibrate()
    print("Done.")

    us_feature_across = UltraSoundFeatureWalkThrough(ub_across, 0.15)
    us_feature_motion = UltraSoundFeatureMotion(ub_across, 3)

    try:
        while True:
            ub_across.update()
            ub_along.update()
            print(f"us_feature_across: {us_feature_across.has_motion()}")
            print(f"us_feature_motion: {us_feature_motion.has_motion()}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        gpio.cleanup()

    sys.exit(0)

