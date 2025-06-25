# Vernier FSR Logger

This Python script reads real-time pressure data from a connected **Arduino** device using **FSR (Force-Sensitive Resistor)** sensors and a **Vernier Force Plate**, then logs it to a CSV file in two formats:

- A raw log with timestamps and full serial output.
- A clean, numeric-only CSV with structured sensor values.


## 📦 Requirements

- Python 3.7+
- Arduino with Vernier force sensor sketch uploaded
- Installed Python packages:
  ```bash
  pip install pyserial
    ````


## 🛠 Setup

Ensure your Arduino is connected and recognized as a serial device, e.g.:

* macOS: `/dev/cu.usbmodem1101`
* Windows: `COM3`
* Linux: `/dev/ttyACM0`


## 🚀 Usage

### Run the script

```bash
python3 main.py --csv --delay 5 --duration 60
```

### Available options

| Option       | Description                              | Default |
| ------------ | ---------------------------------------- | ------- |
| `--csv`      | Save output to raw + clean CSV files     | `False` |
| `--delay`    | Delay (in seconds) before logging starts | `0`     |
| `--duration` | Duration (in seconds) to log data        | `30`    |
| `--baud`     | Baud rate for serial connection          | `9600`  |
| `--timeout`  | Timeout for serial reads                 | `1.0`   |
| `--name`     | Name of experiment; files saved to `hta/<name>/` | `None` |


## 📁 Output

If `--csv` is used, two files will be saved. Without `--name` they are
named `vernier_log_YYYYMMDD_HHMMSS.csv` and `vernier_clean_YYYYMMDD_HHMMSS.csv`.
When `--name <exp>` is provided, files are stored in `hta/<exp>/` as
`<exp>_raw_<timestamp>.csv` and `<exp>_clean_<timestamp>.csv`.

The clean CSV has the following format:

```csv
Time(s),Force(N),DeltaF(N),FSR1,FSR2,FSR3
7.19,16.611,-1.011,1023,1023,1023
7.30,17.622,1.011,1023,1023,1023
...
```


## 🧪 Example

```bash
python3 main.py --csv --delay 2 --duration 15
```

This will:

1. Wait 2 seconds
2. Log pressure data for 15 seconds
3. Save both the raw and clean CSV files


## Exit

Press `Ctrl+C` at any time to manually stop logging early.


## Contact

For bugs or feature requests, open an issue or reach out to the author.

```

