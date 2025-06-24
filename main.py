import sys
import threading
import time
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

    def start_logging(self):
        """Tell the Arduino to start sending data."""
        if not self.is_logging:
            self.ser.write(b's')
            self.is_logging = True

    def stop_logging(self):
        """Tell the Arduino to stop sending data."""
        if self.is_logging:
            self.ser.write(b'e')
            self.is_logging = False

    def _reader_loop(self):
        """Continuously read lines from Arduino and print them."""
        while True:
            line = self.ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {line}")

    def run(self):
        t = threading.Thread(target=self._reader_loop, daemon=True)
        t.start()

        self.start_logging()
        print("▶Logging started automatically. Type 'e' + ↵ to STOP, Ctrl+C to quit.")
        
        try:
            while True:
                cmd = sys.stdin.readline().strip().lower()
                if cmd == 'e':
                    self.stop_logging()
                time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            print("\n⚡ Exiting…")
        finally:
            self.ser.close()

if __name__ == "__main__":
    logger = VernierFSRLogger(baud=9600, timeout=1.0)
    logger.run()
