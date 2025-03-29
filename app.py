from flask import Flask, jsonify
import time
import psutil
import threading
import queue
from prometheus_client import Counter, Gauge, start_http_server

app = Flask(__name__)
request_queue = queue.Queue()

# Prometheus metrics
http_requests_total = Counter('http_requests_total', 'Total HTTP requests')
cpu_usage = Gauge('cpu_usage', 'CPU usage percentage')
memory_usage = Gauge('memory_usage', 'Memory usage percentage')
queue_size = Gauge('queue_size', 'Current queue size')

def update_metrics():
    while True:
        cpu_usage.set(psutil.cpu_percent())
        memory_usage.set(psutil.virtual_memory().percent)
        queue_size.set(request_queue.qsize())
        time.sleep(1)

@app.route('/')
def home():
    return jsonify({"status": "healthy"})

@app.route('/metrics')
def metrics():
    return jsonify({
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "queue_length": request_queue.qsize()
    })

@app.route('/load/cpu')
def load_cpu():
    # Start CPU intensive task
    thread = threading.Thread(target=cpu_intensive_task)
    thread.daemon = True
    thread.start()
    return jsonify({"message": "CPU load started"})

@app.route('/load/memory')
def load_memory():
    # Start memory intensive task
    thread = threading.Thread(target=memory_intensive_task)
    thread.daemon = True
    thread.start()
    return jsonify({"message": "Memory load started"})

@app.route('/load/http')
def load_http():
    # Simulate HTTP request load
    for _ in range(10):  # Add 10 requests at once
        request_queue.put(1)
        http_requests_total.inc()
    return jsonify({"message": "HTTP requests queued"})

def cpu_intensive_task():
    while True:
        # Simulate CPU load
        [i * i for i in range(10000)]

def memory_intensive_task():
    # Simulate memory load
    large_list = []
    while True:
        # Allocate 50MB at a time
        large_list.append([0] * (50 * 1024 * 1024))
        time.sleep(0.1)

if __name__ == '__main__':
    # Start Prometheus metrics server
    start_http_server(8000)
    # Start metrics update thread
    metrics_thread = threading.Thread(target=update_metrics)
    metrics_thread.daemon = True
    metrics_thread.start()
    # Start Flask app
    app.run(host='0.0.0.0', port=80) 