import sys
import threading
import time
import csv
import argparse
import re
from datetime import datetime

import serial
from code.conn.detector import (
    find_arduino_ports,
    ArduinoNotFoundError,
    MultipleArduinoPortsFoundError,
)

POLL_INTERVAL = 0.01  

class VernierFSRLogger:
    def __init__(self, baud=9600, timeout=1.0):
        try:
            p = find_arduino_ports()
        except ArduinoNotFoundError:
            sys.exit("No Arduino found. Plug it in and try again.")
        except MultipleArduinoPortsFoundError as e:
            sys.exit(f"Multiple Arduinos found: {e.ports!r}")
        self.port = p if isinstance(p, str) else p[0]
        print(f"→ Opening {self.port} @ {baud} baud")
        self.ser = serial.Serial(self.port, baudrate=baud, timeout=timeout)
        time.sleep(2)               # let Arduino reboot
        self.ser.reset_input_buffer()
        self.is_logging = False
        self._stop_reader = threading.Event()
        self._data_lines = []

    def start_logging(self):
        if not self.is_logging:
            self.ser.write(b's')
            self.is_logging = True

    def stop_logging(self):
        if self.is_logging:
            self.ser.write(b'e')
            self.is_logging = False

    def _reader_loop(self):
        while not self._stop_reader.is_set():
            line = self.ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                timestamped_line = f"[{datetime.now().strftime('%H:%M:%S')}] {line}"
                print(timestamped_line)
                self._data_lines.append(timestamped_line)
            else:
                time.sleep(POLL_INTERVAL)

    def run_for(self, duration_seconds: float, start_delay: float = 0):
        t = threading.Thread(target=self._reader_loop, daemon=True)
        t.start()

        if start_delay > 0:
            print(f"⏳ Waiting {start_delay}s before starting logging...")
            time.sleep(start_delay)

        print(f"▶ Logging started for {duration_seconds}s...")
        self.start_logging()

        try:
            time.sleep(duration_seconds)
        except KeyboardInterrupt:
            print("\n🛑 Interrupted!")
        finally:
            self.stop_logging()
            self._stop_reader.set()
            self.ser.close()
            print("⏹ Logging stopped.")

    def save_to_csv(self, filename=None):
        if not filename:
            filename = f"vernier_log_{datetime.now():%Y%m%d_%H%M%S}.csv"

        with open(filename, "w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["timestamped_line"])
            for line in self._data_lines:
                writer.writerow([line])

        print(f"💾 Saved log to {filename}")
        return filename
    
    def save_clean_csv(self, filename=None):
        """
        Parse self._data_lines to extract clean numeric sensor data,
        and save to a neat CSV file.
        """
        if filename is None:
            filename = f"vernier_clean_{datetime.now():%Y%m%d_%H%M%S}.csv"

        pattern = re.compile(
            r"^\s*([\d.]+), Force\(N\): ([\d.\-]+), ΔF\(N\): ([\d.\-]+), "
            r"FSR1: (\d+), FSR2: (\d+), FSR3: (\d+)"
        )

        extracted_rows = []
        for line in self._data_lines:
            if line.startswith('['):
                try:
                    line = line.split('] ', 1)[1]
                except IndexError:
                    continue

            match = pattern.match(line)
            if match:
                extracted_rows.append(match.groups())

        if not extracted_rows:
            print("⚠️ No valid sensor data found to save.")
            return None

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Time(s)", "Force(N)", "DeltaF(N)", "FSR1", "FSR2", "FSR3"])
            writer.writerows(extracted_rows)

        print(f"💾 Saved clean CSV to: {filename}")
        return filename

def parse_args():
    parser = argparse.ArgumentParser(description="Vernier FSR Logger CLI")
    parser.add_argument(
        "--csv", action="store_true",
        help="Save session log to CSV file after completion"
    )
    parser.add_argument(
        "--delay", type=float, default=0,
        help="Seconds to wait before starting logging"
    )
    parser.add_argument(
        "--duration", type=float, default=30,
        help="Duration in seconds to log data"
    )
    parser.add_argument(
        "--baud", type=int, default=9600,
        help="Serial baud rate"
    )
    parser.add_argument(
        "--timeout", type=float, default=1.0,
        help="Serial read timeout (seconds)"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    logger = VernierFSRLogger(baud=args.baud, timeout=args.timeout)
    logger.run_for(duration_seconds=args.duration, start_delay=args.delay)
    if args.csv:
        logger.save_to_csv()
        logger.save_clean_csv()

