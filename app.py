from flask import Flask, jsonify
from prometheus_client import Counter, Gauge, start_http_server
import psutil
import queue
import threading
import time

# --- Flask App ---
app = Flask(__name__)

# --- Request Queue ---
request_queue = queue.Queue(maxsize=50)

# --- Prometheus Metrics ---
http_requests_total = Counter('http_requests_total', 'Total HTTP requests')
cpu_usage = Gauge('cpu_usage', 'Current CPU usage percentage')
memory_usage = Gauge('memory_usage', 'Current memory usage percentage')
queue_size = Gauge('queue_size', 'Current number of requests in the queue')

# --- Background Queue Processor ---
def process_queue():
    while True:
        try:
            request_queue.get(timeout=1)
            time.sleep(0.05)  # Simulate processing
            request_queue.task_done()
        except queue.Empty:
            continue

threading.Thread(target=process_queue, daemon=True).start()

# --- Routes ---
@app.route('/')
def index():
    http_requests_total.inc()
    cpu_usage.set(psutil.cpu_percent())
    memory_usage.set(psutil.virtual_memory().percent)
    queue_size.set(request_queue.qsize())
    
    try:
        request_queue.put_nowait(1)
    except queue.Full:
        return jsonify({"message": "Queue full"}), 503
    
    return jsonify({"message": "Hello, metrics are updating!"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

# --- Start Prometheus metrics server ---
if __name__ == "__main__":
    start_http_server(8000)  # Prometheus scrapes metrics here
    app.run(host='0.0.0.0', port=5000)
