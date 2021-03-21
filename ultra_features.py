#!/usr/bin/env python3
import sys
import time
import math
import RPi.GPIO as gpio

from ultra_sound import UltraSound
from kalman_filter import KalmanFilter

us_hall = UltraSound(trigger_pin=17, echo_pin=27)
us_bath = UltraSound(trigger_pin=23, echo_pin=24)

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

class UltraSoundFilter(object):
    def __init__(self, us):
        self.ultra_sound = us

        self.kalman_filter = None
        self.last_update_time = None

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
        self.kalman_filter = KalmanFilter(self.calibration_range, self.calibration_std)

    def update(self):
        """ Update the internal feature based on sensor data. """
        cur_dist = self.ultra_sound.get_distance()
        now = time.time()
        if cur_dist is None:
            return
        if self.last_update_time is None:
            delta_t = 0
        else:
            delta_t = now - self.last_update_time
        self.kalman_filter.predict(delta_t)
        self.kalman_filter.correct(cur_dist)
        self.last_update_time = now

    def get_distance(self):
        if self.kalman_filter is None:
            return None
        return self.kalman_filter.distance()


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

class UltraSoundFeatureWalkThroughFiltered(UltraSoundFeatures):
    def __init__(self, ultra_filter, max_detection_threshold=0, min_detection_time=0):
        super().__init__(ultra_filter)
        self.max_detection_threshold = max_detection_threshold
        self.min_detection_time = min_detection_time

        self.detection_start_time = None
        self.detection_end_time = None

    def has_motion(self):
        """ Return if motion was detected. """
        dist = self.ultra_sound_buffer.kalman_filter.distance()
        if not dist:
            return False
        ts = time.time()

        if dist < self.max_detection_threshold:
            if self.detection_start_time is None:   # new interval
                self.detection_start_time = ts
                self.detection_end_time = ts
            else:                       # continue/expand interval
                self.detection_end_time = ts
        elif self.detection_start_time is not None:
            #if end_feature - start_feature >= min_feature_time:
            #    feature_intervals.append((start_feature, end_feature))
            self.detection_start_time  = None
            self.detection_end_time = None

        if self.detection_start_time is not None:
            detection_time = self.detection_end_time - self.detection_start_time
        else:
            detection_time = -1.
        print(f"Distance: {dist:.2f}m < {self.max_detection_threshold:.2f}m? Interval: [{self.detection_start_time}, {self.detection_end_time}] ({detection_time}s)")
        if self.detection_start_time is not None:
            return detection_time >= self.min_detection_time
        else:
            return False

if __name__ == '__main__':
    ub_hall = UltraSoundBuffer(us_hall)
    ub_bath = UltraSoundBuffer(us_bath)
    uf_hall = UltraSoundFilter(us_hall)
    uf_bath = UltraSoundFilter(us_bath)
    print("Calibrating...")
    ub_hall.calibrate()
    ub_bath.calibrate()
    uf_hall.calibrate()
    uf_bath.calibrate()
    print("Done.")

    us_feature_hall = UltraSoundFeatureWalkThrough(ub_hall, 0.3)
    us_feature_hall_filtered = UltraSoundFeatureWalkThroughFiltered(uf_hall, 1.0, 0.2)
    us_feature_bath_filtered = UltraSoundFeatureWalkThroughFiltered(uf_bath, 1.0, 0.2)

    try:
        while True:
            ub_hall.update()
            ub_bath.update()
            uf_hall.update()
            uf_bath.update()
            print(f"Filtered    Hall: {uf_hall.get_distance():.2f}\tBath: {uf_bath.get_distance():.2f}")
            hall_avg = sum(ub_hall.get_distances())/len(ub_hall.get_distances())
            bath_avg = sum(ub_bath.get_distances())/len(ub_bath.get_distances())
            print(f"Averaged    Hall: {hall_avg:.2f}\tBath: {bath_avg:.2f}")
            print(f"Max         Hall: {max(ub_hall.get_distances()):.2f}\tBath: {max(ub_bath.get_distances()):.2f}")
            print(f"us_feature_hall: {us_feature_hall.has_motion()}")
            print(f"us_feature_hall_filtered: {us_feature_hall_filtered.has_motion()}")
            print(f"us_feature_bath_filtered: {us_feature_bath_filtered.has_motion()}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        gpio.cleanup()

    sys.exit(0)

