import serial
import time
import csv
import json
from datetime import datetime
from collections import deque

class AdvancedFSRController:
    def __init__(self, port='/dev/cu.usbmodem1101', baud_rate=9600):
        self.port = port
        self.baud_rate = baud_rate
        self.arduino = None
        self.is_connected = False
        self.is_monitoring = False
        
        self.fsr_history = deque(maxlen=1000)  
        self.session_data = list()
        
        self.stats = {
            'total_readings': 0,
            'max_pressure': 0,
            'min_pressure': 1023,
            'avg_pressure': 0,
            'session_start': None,
            'pressure_events': {
                'light_touches': 0,
                'light_squeezes': 0,
                'medium_squeezes': 0,
                'strong_squeezes': 0
            }
        }
        
    def connect(self):
        """Connect to Arduino"""
        try:
            self.arduino = serial.Serial(self.port, self.baud_rate)
            time.sleep(2)
            self.is_connected = True
            self.stats['session_start'] = datetime.now()
            print(f"Connected to Arduino on {self.port}")
            print(f"Session started at {self.stats['session_start'].strftime('%H:%M:%S')}")
            return True
        except serial.SerialException as e:
            print(f"Connection failed: {e}")
            return False
    
    def update_statistics(self, fsr_value, pressure_category):
        """Update running statistics"""
        self.stats['total_readings'] += 1
        self.stats['max_pressure'] = max(self.stats['max_pressure'], fsr_value)
        self.stats['min_pressure'] = min(self.stats['min_pressure'], fsr_value)
        
        total_sum = sum(self.fsr_history) + fsr_value
        self.stats['avg_pressure'] = total_sum / len(self.fsr_history) if self.fsr_history else fsr_value
        
        if pressure_category in self.stats['pressure_events']:
            self.stats['pressure_events'][pressure_category] += 1
    
    def create_data_entry(self, fsr_value, pressure_category, pressure_label):
        """Create a data entry for logging"""
        return {
            'timestamp': datetime.now().isoformat(),
            'fsr_value': fsr_value,
            'pressure_category': pressure_category,
            'pressure_label': pressure_label,
            'reading_number': self.stats['total_readings']
        }
    
    def save_to_csv(self, filename=None):

        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"fsr_session_{timestamp}.csv"
        
        with open(filename, 'w', newline='') as csvfile:
            if self.session_data:
                fieldnames = self.session_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.session_data)
                print(f"📊 Data saved to {filename}")
                return filename
        return None
    
    def save_to_json(self, filename=None):
        """Save session data and statistics to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"fsr_session_{timestamp}.json"
        
        session_summary = {
            'session_info': {
                'start_time': self.stats['session_start'].isoformat() if self.stats['session_start'] else None,
                'end_time': datetime.now().isoformat(),
                'duration_seconds': (datetime.now() - self.stats['session_start']).total_seconds() if self.stats['session_start'] else 0,
                'arduino_port': self.port
            },
            'statistics': self.stats,
            'data': self.session_data
        }
        
        with open(filename, 'w') as jsonfile:
            json.dump(session_summary, jsonfile, indent=2)
            print(f"📋 Session summary saved to {filename}")
            return filename
        return None
    
    def print_live_stats(self):
        """Print live statistics"""
        if self.stats['total_readings'] > 0:
            print(f"\n LIVE STATS:")
            print(f"   Readings: {self.stats['total_readings']}")
            print(f"   Current: {self.fsr_history[-1] if self.fsr_history else 0}")
            print(f"   Max: {self.stats['max_pressure']}")
            print(f"   Min: {self.stats['min_pressure']}")
            print(f"   Avg: {self.stats['avg_pressure']:.1f}")
            print(f"   Events: L:{self.stats['pressure_events']['light_touch']} "
                  f"LS:{self.stats['pressure_events']['light_squeeze']} "
                  f"M:{self.stats['pressure_events']['medium_squeeze']} "
                  f"S:{self.stats['pressure_events']['strong_squeeze']}")
            print("-" * 50)
    
    def monitor_fsr(self, duration_seconds=None, log_to_file=True, show_stats_interval=10):
        """Main monitoring function with advanced features"""
        if not self.is_connected:
            print("Arduino not connected!")
            return
        
        self.is_monitoring = True
        start_time = time.time()
        last_stats_time = start_time
        
        print(" FSR monitoring started... | Commands: Ctrl+C to stop")
        print("=" * 60)
        
        try:
            while self.is_monitoring:
                # Check duration limit
                if duration_seconds and (time.time() - start_time) > duration_seconds:
                    print(f"⏰ Monitoring completed ({duration_seconds}s)")
                    break
                
                # Read Arduino data
                if self.arduino.in_waiting > 0:
                    line = self.arduino.readline().decode('utf-8').strip()
                    
                    if line.startswith("FSR Reading:"):
                        fsr_value = int(line.split(": ")[1])
                        
                        # Classify pressure
                        pressure_category, pressure_label, emoji = self.classify_pressure(fsr_value)
                        
                        # Update data structures
                        self.fsr_history.append(fsr_value)
                        self.update_statistics(fsr_value, pressure_category)
                        
                        # Create data entry
                        data_entry = self.create_data_entry(fsr_value, pressure_category, pressure_label)
                        self.session_data.append(data_entry)
                        
                        # Display reading
                        timestamp = datetime.now().strftime('%H:%M:%S')
                        print(f"[{timestamp}] {emoji} FSR: {fsr_value:4d} | {pressure_label}")
                        
                        # Special alerts
                        if fsr_value > 950:
                            print("🚨 EXTREME PRESSURE DETECTED!")
                        elif fsr_value > 800:
                            print("⚠️  High pressure warning")
                        
                        # Periodic statistics
                        if time.time() - last_stats_time > show_stats_interval:
                            self.print_live_stats()
                            last_stats_time = time.time()
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping monitoring...")
        
        finally:
            self.is_monitoring = False
            
            print("\n" + "=" * 60)
            print("📊 FINAL SESSION SUMMARY")
            print("=" * 60)
            self.print_live_stats()
            
            if log_to_file and self.session_data:
                csv_file = self.save_to_csv()
                json_file = self.save_to_json()
                print(f"💾 Files saved: {csv_file}, {json_file}")
    
    def disconnect(self):
        """Disconnect from Arduino"""
        self.is_monitoring = False
        if self.arduino:
            self.arduino.close()
            self.is_connected = False
            print("🔌 Arduino disconnected")

if __name__ == "__main__":
    fsr = AdvancedFSRController(port='/dev/cu.usbmodem1101')
    
    if fsr.connect():
        try:
            fsr.monitor_fsr(log_to_file=True, show_stats_interval=15)
            
        finally:
            fsr.disconnect()
    else:
        print("Failed to connect to Arduino")
