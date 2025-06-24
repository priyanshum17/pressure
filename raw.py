import sys
import time
import csv
import argparse
from datetime import datetime

import serial
from code.conn.detector import (
    find_arduino_ports,
    ArduinoNotFoundError,
    MultipleArduinoPortsFoundError,
)

def parse_args():
    p = argparse.ArgumentParser(
        description="Read from one or more Arduinos and optionally log to CSV"
    )
    p.add_argument(
        "--csv", action="store_true",
        help="Enable CSV logging of (epoch, port, sensor, reading)"
    )
    p.add_argument(
        "--csvfile", type=str, default=None,
        help="Path to CSV file (defaults to readings_<timestamp>.csv)"
    )
    p.add_argument(
        "--baud", type=int, default=9600,
        help="Serial baud rate"
    )
    p.add_argument(
        "--timeout", type=float, default=1.0,
        help="Serial read timeout (seconds)"
    )
    return p.parse_args()


def open_ports(ports, baud, timeout):
    conns = []
    for port in ports:
        try:
            ser = serial.Serial(port, baudrate=baud, timeout=timeout)
            time.sleep(2)
            ser.reset_input_buffer()
            conns.append((port, ser))
            print(f"Connected to {port}")
        except serial.SerialException as e:
            print(f"Failed to connect {port}: {e}", file=sys.stderr)
    return conns


def parse_readings(line):
    """
    Parse a line of serial input into a dict of sensor readings.

    Expected formats:
      - "A0:512,A1:256,A2:128"
      - "512,256,128" (assumes default sensor names: S1, S2, ...)
    """
    readings = {}
    parts = [p.strip() for p in line.split(',') if p.strip()]

    if all(':' in p for p in parts):
        for p in parts:
            sensor, val = p.split(':', 1)
            try:
                readings[sensor.strip()] = int(val.strip())
            except ValueError:
                continue
    else:
        for idx, val in enumerate(parts, start=1):
            try:
                readings[f"S{idx}"] = int(val)
            except ValueError:
                continue
    return readings


def main():
    args = parse_args()

    try:
        found = find_arduino_ports()
    except ArduinoNotFoundError:
        print("No Arduino found. Is it plugged in?", file=sys.stderr)
        sys.exit(1)
    except MultipleArduinoPortsFoundError as e:
        print("Multiple Arduinos detected:", e.ports)
        ports = e.ports
    else:
        ports = [found] if isinstance(found, str) else found

    print(f"→ Using ports: {ports}")

    conns = open_ports(ports, args.baud, args.timeout)
    if not conns:
        print("No serial connections could be opened.", file=sys.stderr)
        sys.exit(1)

    csv_writer = None
    csv_file = None
    if args.csv:
        fname = args.csvfile or f"readings_{datetime.now():%Y%m%d_%H%M%S}.csv"
        csv_file = open(fname, "w", newline="")
        writer = csv.writer(csv_file)
        writer.writerow(["epoch", "port", "sensor", "reading"])
        csv_writer = writer
        print(f"Logging to CSV: {fname}")

    try:
        print("Starting read loop (Ctrl+C to stop)…")
        while True:
            for port, ser in conns:
                raw = ser.readline().decode("utf-8", errors="ignore").strip()
                if not raw:
                    continue

                epoch = time.time()
                timestamp = datetime.fromtimestamp(epoch).isoformat()
                readings = parse_readings(raw)

                for sensor, value in readings.items():
                    output = f"[{timestamp}] {port} {sensor}: {value}"
                    print(output)
                    if csv_writer:
                        csv_writer.writerow([epoch, port, sensor, value])

                if csv_file:
                    csv_file.flush()

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopped by user")

    finally:
        for _, ser in conns:
            ser.close()
        if csv_file:
            csv_file.close()
        print("All connections closed.")


if __name__ == "__main__":
    main()
