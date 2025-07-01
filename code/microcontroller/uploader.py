
import subprocess
import sys

def upload_arduino_code(board_fqbn, port, sketch_path):
    """
    Uploads Arduino code to a microcontroller using arduino-cli.

    Args:
        board_fqbn (str): The fully qualified board name (e.g., "arduino:avr:uno").
        port (str): The serial port of the Arduino (e.g., "/dev/cu.usbmodem14101").
        sketch_path (str): The path to the Arduino sketch (.ino file).
    """
    command = [
        "arduino-cli",
        "compile",
        "--fqbn", board_fqbn,
        sketch_path
    ]
    print(f"Compiling sketch: {' '.join(command)}")
    compile_process = subprocess.run(command, capture_output=True, text=True)
    if compile_process.returncode != 0:
        print("Compilation failed:")
        print(compile_process.stderr)
        return
    print("Compilation successful.")

    command = [
        "arduino-cli",
        "upload",
        "--fqbn", board_fqbn,
        "--port", port,
        sketch_path
    ]
    print(f"Uploading sketch: {' '.join(command)}")
    upload_process = subprocess.run(command, capture_output=True, text=True)
    if upload_process.returncode != 0:
        print("Upload failed:")
        print(upload_process.stderr)
        return
    print("Upload successful.")

if __name__ == "__main__":
    # Example Usage:
    # Replace with your board's FQBN, port, and sketch path
    # You can find FQBNs using `arduino-cli board listall`
    # You can find ports using `arduino-cli board list`
    
    # For example, for an Arduino Uno on macOS:
    # BOARD_FQBN = "arduino:avr:uno"
    # PORT = "/dev/cu.usbmodemXXXX"
    # SKETCH_PATH = "/path/to/your/arduino/sketch/your_sketch.ino"

    print("This script requires arduino-cli to be installed and configured.")
    print("Please modify the example usage within the script with your specific board, port, and sketch path.")
    print("Example: python code/microcontroller/uploader.py")

    # Uncomment and modify the following lines to use the function:
    # if len(sys.argv) == 4:
    #     upload_arduino_code(sys.argv[1], sys.argv[2], sys.argv[3])
    # else:
    #     print("Usage: python uploader.py <board_fqbn> <port> <sketch_path>")

