import sys
import re
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_adc.py <logfile>")
        sys.exit(1)

    input_path = sys.argv[1]

    if not os.path.isfile(input_path):
        print(f"File not found: {input_path}")
        sys.exit(1)

    with open(input_path, "r") as f:
        lines = f.readlines()

    collect = False
    adc_values = []

    for line in lines:
        if "Baseline complete. Starting main recording" in line:
            collect = True
            continue
        if collect and "[MAIN]" in line:
            m = re.search(r'ADC:\s*(\d+)', line)
            if m:
                adc_values.append(m.group(1))

    if not adc_values:
        print("No MAIN ADC data found.")
        sys.exit(0)

    # Create output filename
    base_name = os.path.basename(input_path)
    clean_name = f"clean_{base_name}".replace(" ", "_")
    out_path = os.path.join(os.path.dirname(input_path), clean_name)

    with open(out_path, "w") as f:
        f.write("ADC\n")
        for adc in adc_values:
            f.write(f"{adc}\n")

    print(f"Saved {len(adc_values)} ADC values to {out_path}")

if __name__ == "__main__":
    main()