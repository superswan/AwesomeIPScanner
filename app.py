from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import nmap
import eventlet
import os
from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading

eventlet.monkey_patch()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

executor = ThreadPoolExecutor(max_workers=127)
lock = Lock()  # Lock for thread-safe operations on the responsive_ips list

# FRONTEND
# Run frontend in separate thread 
frontend_app = Flask(__name__, static_url_path='/static')

# FRONTEND ROUTES
@frontend_app.route('/')
def serve_static_index():
    return send_from_directory('static', 'index.html')

@frontend_app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


def run_frontend():
    frontend_app.run(port=3000)

def update_progress(current_index=0, ip_count=1):
        progress = (current_index + 1) / ip_count * 100
        print(f"{int(progress)}% complete")
        socketio.emit('update_progress', int(progress))

# BACKEND Code
def nmap_ip(ip, service_scan_list=[], current_index=0, ip_count=1):
    update_progress(current_index, ip_count)
    nm = nmap.PortScanner()
    if service_scan_list:
        services_str = ','.join(service_scan_list)
        print(f"Scanning {ip} ({current_index}/{ip_count}) for services {services_str}...")
        scan_args = f'-p {services_str} -T4 --min-parallelism 64 --max-parallelism 256 --host-timeout 15s --max-retries 1'

    else:
        print(f"Ping scanning {ip}...")
        scan_args = '-sn'  # Ping scan

    nm.scan(hosts=ip, arguments=scan_args)
    if ip in nm.all_hosts():  # Check if the IP exists in the scan results
        state = nm[ip].state()
        if state == 'up':
            print(f"{ip} is up")
            name = nm[ip].hostname()

            if 'vendor' in nm[ip] and nm[ip]['vendor']:
                manufacturer = next(iter(nm[ip]['vendor'].values()))
            else:
                manufacturer = 'N/A'
            
            mac = nm[ip]['addresses']['mac'] if 'mac' in nm[ip]['addresses'] else 'N/A'

            detected_services = {}
            for service in service_scan_list:
                if 'tcp' in nm[ip] and int(service) in nm[ip]['tcp']:
                    detected_services[service] = nm[ip]['tcp'][int(service)]['state']

            print(f"{ip}: {detected_services}")
            
            result = {
                "status": "Up",
                "name": name,
                "IP": ip,
                "manufacturer": manufacturer,
                "mac": mac,
                "services": detected_services
            }

            socketio.emit('scan_data', result)
            return result
    return None

# ROUTES
@app.route('/scan', methods=['POST'])
def scan_ips():

    service_scan = request.form.getlist('services')
    print(service_scan)

    ip_range = request.form['ip_range']
    if '-' in ip_range:
        start_ip, end_suffix = ip_range.split('-')
        base_ip = ".".join(start_ip.split('.')[:-1])
        start_last_octet = int(start_ip.split('.')[-1])
        end_last_octet = int(end_suffix)
    else:
        start_ip = ip_range
        base_ip = ".".join(start_ip.split('.')[:-1])
        start_last_octet = int(start_ip.split('.')[-1])
        end_last_octet = start_last_octet

    ips = [f"{base_ip}.{i}" for i in range(start_last_octet, end_last_octet + 1)]
    ip_count = len(ips)
    
    # Use the executor to parallelize the IP pinging
    responsive_data = []  # This list will store responsive IPs
    futures = [executor.submit(nmap_ip, ip, service_scan, index, ip_count) for index, ip in enumerate(ips)]
    for future in futures: 
        result = future.result()
        if result:  # If we got a result dictionary, append to the list
            with lock:
                responsive_data.append(result)
            
    return jsonify(responsive_data)

@socketio.on('connect')
def handle_connection():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnection():
    print('Client disconnected')

if __name__ == '__main__':
    threading.Thread(target=run_frontend).start()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
