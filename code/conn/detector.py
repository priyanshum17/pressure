import sys
import serial.tools.list_ports
from typing import Optional, Union, List

class ArduinoNotFoundError(Exception):
    """Raised when no Arduino is found on any serial port."""
    pass

class MultipleArduinoPortsFoundError(Exception):
    """Raised when more than one Arduino is detected."""
    def __init__(self, ports: List[str]):
        super().__init__(f"Multiple Arduino ports found: {ports}")
        self.ports = ports

def find_arduino_ports() -> Union[str, List[str]]:
    """
    Scan the system's serial ports and identify Arduino devices.

    Uses USB vendor/product IDs, device descriptions, and platform-specific
    naming conventions to detect Arduino ports.

    Raises:
        ArduinoNotFoundError: if no Arduino devices are found.
        MultipleArduinoPortsFoundError: if more than one Arduino is found.
    Returns:
        - A single port name (str) if exactly one Arduino device is found.
        - A list of port names (List[str]) if multiple Arduino devices are found.
    """
    arduino_ports: List[str] = []
    ports = list(serial.tools.list_ports.comports())

    arduino_vid_pid = [
        (0x2341, 0x0043),  # Uno
        (0x2341, 0x0001),
        (0x2341, 0x0243),  # Leonardo
        (0x2341, 0x8036),  # Mega 2560
        (0x2341, 0x804d),  # Mega ADK
        (0x2341, 0x804e),  # Leonardo ETH
        (0x10C4, 0xEA60),  # CP210x UART Bridge
        (0x1A86, 0x7523),  # CH340 converter
    ]

    for port in ports:
        nm = port.device
        desc = (port.description or "").lower()
        man = (port.manufacturer or "").lower()
        vid, pid = port.vid, port.pid

        if (vid, pid) in arduino_vid_pid:
            arduino_ports.append(nm)
            continue
        if "arduino" in desc or "arduino" in man:
            arduino_ports.append(nm)
            continue

        if sys.platform.startswith("darwin") and (nm.startswith("/dev/cu.usbmodem") or nm.startswith("/dev/cu.usbserial")):
            arduino_ports.append(nm)
        elif sys.platform.startswith("linux") and (nm.startswith("/dev/ttyACM") or nm.startswith("/dev/ttyUSB")):
            arduino_ports.append(nm)
        elif sys.platform.startswith("win") and "arduino" in desc:
            arduino_ports.append(nm)

    if not arduino_ports:
        raise ArduinoNotFoundError()
    if len(arduino_ports) > 1:
        raise MultipleArduinoPortsFoundError(arduino_ports)

    return arduino_ports[0]
