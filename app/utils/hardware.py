import serial
import serial.tools.list_ports
import time
import json
import threading
import datetime

# Global singleton or shared state can be imported here, 
# but we'll return data via method access to keep it clean.

class HardwareReader:
    def __init__(self):
        self.serial_port = None
        self.baud_rate = 9600
        self.running = True
        self.log_file = "vitals_log.json"
        self.latest_data = {"heart_rate": 0, "oxygen": 0, "active": False}
        
        # Start background thread
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def get_latest(self):
        return self.latest_data

    def _run_loop(self):
        print("[Hardware] Starting Serial Monitor Service...")
        
        while self.running:
            if not self.serial_port:
                self._scan_and_connect()
            else:
                self._read_data()
            
            time.sleep(1)

    def _scan_and_connect(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            # Simple heuristic: try to connect to the first available USB-Serial device
            try:
                print(f"[Hardware] Attempting connection to {port.device}...")
                self.serial_port = serial.Serial(port.device, self.baud_rate, timeout=1)
                print(f"[Hardware] Connected to {port.device}")
                self.latest_data["active"] = True
                return
            except Exception as e:
                print(f"[Hardware] Connection failed: {e}")
        
        # If no ports found
        self.latest_data["active"] = False
        time.sleep(2) # Wait before retry

    def _read_data(self):
        try:
            if self.serial_port.in_waiting > 0:
                line = self.serial_port.readline().decode('utf-8').strip()
                if line:
                    self._parse_line(line)
        except Exception as e:
            print(f"[Hardware] Read Error: {e}")
            if self.serial_port:
                self.serial_port.close()
            self.serial_port = None
            self.latest_data["active"] = False

    def _parse_line(self, line):
        # Expected Format: "HR:75,SPO2:98"
        try:
            parts = line.split(',')
            data = {}
            for part in parts:
                key, val = part.split(':')
                data[key.strip()] = int(val.strip())
            
            if 'HR' in data and 'SPO2' in data:
                # Update State
                self.latest_data['heart_rate'] = data['HR']
                self.latest_data['oxygen'] = data['SPO2']
                self.latest_data['active'] = True
                
                # Log to JSON
                self._log_to_json(data)
                
        except Exception as e:
            # print(f"[Hardware] Parse Error: {line} -> {e}") 
            pass

    def _log_to_json(self, data):
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "heart_rate": data.get('HR'),
            "oxygen": data.get('SPO2')
        }
        
        try:
            try:
                with open(self.log_file, 'r') as f:
                    logs = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                logs = []
            
            # Ignore invalid readings
            if not data.get('HR') or int(data.get('HR')) <= 0:
                print(f"[Hardware] Ignoring invalid HR: {data.get('HR')}")
                return

            logs.append(entry)
            
            if len(logs) > 1000:
                logs = logs[-1000:]
                
            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            print(f"Log Error: {e}")

    def stop(self):
        self.running = False
        if self.serial_port:
            self.serial_port.close()

# Create global instance
hardware_service = HardwareReader()
