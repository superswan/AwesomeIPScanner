import eventlet
eventlet.monkey_patch()
from flask_socketio import SocketIO, emit
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, send_from_directory
from flask_cors import CORS
import nmap
import threading
from threading import Lock

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

nm = nmap.PortScanner()

executor = ThreadPoolExecutor(max_workers=20)
lock = Lock()  # Lock for thread-safe operations on the responsive_ips list

# Run frontend in separate thread 
frontend_app = Flask(__name__, static_url_path='/static')

@frontend_app.route('/')
def serve_static_index():
    return send_from_directory('static', 'index.html')

def run_frontend():
    frontend_app.run(port=3000)

def ping_ip(ip):
    print(ip)
    nm.scan(hosts=ip, arguments='-sn')  # -sn: Ping scan, disables port scan
    if ip in nm.all_hosts():  # Check if the IP exists in the scan results
        state = nm[ip].state()
        if state == 'up':
            name = nm[ip].hostname()

            if 'vendor' in nm[ip] and nm[ip]['vendor']:
                manufacturer = next(iter(nm[ip]['vendor'].values()))
            else:
                manufacturer = None
            
            mac = nm[ip]['addresses']['mac'] if 'mac' in nm[ip]['addresses'] else None

            result = {
                "status": "Up",
                "name": name,
                "IP": ip,
                "manufacturer": manufacturer,
                "mac": mac
            }

            socketio.emit('scan_data', result)
            return result
    return None

@app.route('/scan', methods=['POST'])
def scan_ips():
    responsive_data = []  # This list will store responsive IPs

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

    # Use the executor to parallelize the IP pinging
    results = list(executor.map(ping_ip, ips))
    for result in results:
        if result:  # If we got a result dictionary, append to the list
            with lock:
                responsive_data.append(result)

    # Render the IPs as an HTML list
    table_rows = "\n".join(
        [f"<tr><td>{entry['status']}</td><td>{entry['name']}</td><td>{entry['IP']}</td><td>{entry['manufacturer']}</td><td>{entry['mac']}</td></tr>" for entry in responsive_data]
    )
    html_content = f'{table_rows}'

    return html_content

@socketio.on('connect')
def handle_connection():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnection():
    print('Client disconnected')

if __name__ == '__main__':
    threading.Thread(target=run_frontend).start()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
