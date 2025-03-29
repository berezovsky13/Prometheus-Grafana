from flask import Flask, jsonify
import time
import psutil
import threading
import queue

app = Flask(__name__)
request_queue = queue.Queue()

def cpu_intensive_task():
    while True:
        # Simulate CPU load
        [i * i for i in range(10000)]

def memory_intensive_task():
    # Simulate memory load
    large_list = []
    while True:
        large_list.append([0] * 1000000)
        time.sleep(0.1)

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
    request_queue.put(1)
    return jsonify({"message": "HTTP request queued"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80) 