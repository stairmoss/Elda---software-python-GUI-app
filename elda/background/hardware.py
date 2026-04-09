import serial
import serial.tools.list_ports
import time
import json
import threading
import datetime
from elda.ai.state import app_state

class HardwareReader:
    def __init__(self):
        self.serial_port = None
        self.baud_rate = 9600
        self.running = True
        self.log_file = "vitals_log.json"
        
        # Start background thread
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

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
            # In production, check for specific VID/PID
            try:
                print(f"[Hardware] Attempting connection to {port.device}...")
                self.serial_port = serial.Serial(port.device, self.baud_rate, timeout=1)
                print(f"[Hardware] Connected to {port.device}")
                app_state.hardware_connected = True
                return
            except Exception as e:
                print(f"[Hardware] Connection failed: {e}")
        
        # If no ports found
        app_state.hardware_connected = False
        time.sleep(2) # Wait before retry

    def _read_data(self):
        try:
            if self.serial_port.in_waiting > 0:
                line = self.serial_port.readline().decode('utf-8').strip()
                if line:
                    self._parse_line(line)
        except Exception as e:
            print(f"[Hardware] Read Error: {e}")
            self.serial_port.close()
            self.serial_port = None
            app_state.hardware_connected = False

    def _parse_line(self, line):
        # Expected Format: "HR:75,SPO2:98"
        try:
            parts = line.split(',')
            data = {}
            for part in parts:
                key, val = part.split(':')
                data[key.strip()] = int(val.strip())
            
            if 'HR' in data and 'SPO2' in data:
                # Update App State
                app_state.vitals['heart_rate'] = data['HR']
                app_state.vitals['oxygen'] = data['SPO2']
                
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
        
        # Simple Append Logic (Not efficient for massive files, but fine for prototype)
        try:
            try:
                with open(self.log_file, 'r') as f:
                    logs = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                logs = []
            
            logs.append(entry)
            
            # Keep last 1000 records
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
