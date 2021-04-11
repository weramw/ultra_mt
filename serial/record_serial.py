#!/usr/bin/env python3
import sys
import os
import time
import csv
import datetime
import serial

if __name__ == "__main__":
    device = sys.argv[1]

    print("Opening Device...")
    dev = serial.Serial(device, 9600)

    print("Done.\nOpening output file...")
    data_log = open("serial_data.csv", 'a', newline='')
    data_writer = csv.writer(data_log, lineterminator='\n')
    print("Done.\nWaiting for data...")

    got_valid_line = False
    try:
        while True:
            try:
                line = dev.readline()
                line = line.decode('utf-8')
                print(line)

                now = time.time()
                parts = line.split()
                if not got_valid_line and len(parts) == 10:
                    print("Got valid line. Starting recording")
                    print(line)
                    got_valid_line = True
                if got_valid_line:
                    if len(parts) == 10:
                        now_date = datetime.datetime.now()
                        data_writer.writerow([now_date, now] + parts)
                        print(".", end="")
                    elif line.strip():   # print invalid non-empty
                        print(f"Got invalid line: {line}")
                    sys.stdout.flush()
                else:
                    print("Waiting for valid line, current is:")
                    print(line)
                time.sleep(0.1)
            except Exception as e:
                print("An error occured:")
                print(e)
                print("Trying to continue")
                time.sleep(0.5)
                continue
    except KeyboardInterrupt:
        print("Closing data file.")
        data_log.close()
