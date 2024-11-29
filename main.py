import requests
import yaml
import time
import threading
from collections import defaultdict
from urllib.parse import urlparse

class EndpointMonitor:
    def __init__(self, config_path):
        self.endpoints = self.load_config(config_path)
        self.domain_availability = defaultdict(lambda: {"up": 0, "total": 0})
    
    def load_config(self, config_path):
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    
    def check_health(self, endpoint):
        url = endpoint.get('url')
        method = endpoint.get('method', 'GET').upper()
        headers = endpoint.get('headers', {})
        data = endpoint.get('body', None)
        
        try:
            start_time = time.time()
            response = requests.request(method, url, headers=headers, data=data, timeout=5)
            latency = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Determine if the endpoint is UP or DOWN
            if 200 <= response.status_code < 300 and latency < 500:
                return "UP"
            else:
                return "DOWN"
        except requests.RequestException:
            return "DOWN"

    def monitor_endpoints(self):
        while True:
            for endpoint in self.endpoints:
                name = endpoint.get('name')
                url = endpoint.get('url')
                domain = urlparse(url).netloc
                status = self.check_health(endpoint)
                
                self.domain_availability[domain]["total"] += 1
                if status == "UP":
                    self.domain_availability[domain]["up"] += 1
            
            
            self.log_availability()
            time.sleep(15)
    
    def log_availability(self):
        for domain, data in self.domain_availability.items():
            total_checks = data["total"]
            up_checks = data["up"]
            availability = round((up_checks / total_checks) * 100) if total_checks > 0 else 0
            print(f"{domain} has {availability}% availability percentage")

def main(config_path):
    monitor = EndpointMonitor(config_path)
    monitor_thread = threading.Thread(target=monitor.monitor_endpoints)
    monitor_thread.daemon = True  # Allows program to exit even if thread is running
    monitor_thread.start()
    
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping endpoint monitor.")

# Replace 'path/to/your/config.yaml' with the actual path to your YAML file
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python endpoint_monitor.py <config_path>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    main(config_path)
