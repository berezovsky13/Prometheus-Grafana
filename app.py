# Import required libraries
from flask import Flask, jsonify  # Flask for web server, jsonify for JSON responses
import time  # For time-related operations
import psutil  # For system and process utilities
import threading  # For running tasks in background
import queue  # For thread-safe queue operations
from prometheus_client import Counter, Gauge, start_http_server  # For Prometheus metrics
import gc  # Add garbage collector

# Initialize Flask application
app = Flask(__name__)
# Create a queue with a maximum size
request_queue = queue.Queue(maxsize=100)  # Limit queue size to 100

# Define Prometheus metrics
# Counter: Only increases, used for counting total requests
http_requests_total = Counter('http_requests_total', 'Total HTTP requests')
# Gauge: Can increase and decrease, used for current values
cpu_usage = Gauge('cpu_usage', 'Current CPU usage percentage')
memory_usage = Gauge('memory_usage', 'Current memory usage percentage')
queue_size = Gauge('queue_size', 'Current number of requests in the queue')

def process_queue():
    while True:
        try:
            # Process requests from queue
            request = request_queue.get(timeout=1)
            time.sleep(0.1)  # Simulate processing
            request_queue.task_done()
            # Force garbage collection after processing each request
            gc.collect()
        except queue.Empty:
            continue

# Start queue processing thread
queue_thread = threading.Thread(target=process_queue, daemon=True)
queue_thread.start()

@app.route('/')
def hello():
    http_requests_total.inc()
    
    # Update metrics
    cpu_usage.set(psutil.cpu_percent())
    memory_usage.set(psutil.virtual_memory().percent)
    queue_size.set(request_queue.qsize())
    
    # Try to add request to queue, skip if full
    try:
        request_queue.put_nowait(1)
    except queue.Full:
        return jsonify({"message": "Queue is full, request dropped"}), 503
    
    return jsonify({"message": "Hello from HPA Demo!"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/metrics')
def metrics():
    """
    Endpoint that returns current system metrics
    Used for debugging and monitoring
    """
    return jsonify({
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "queue_length": request_queue.qsize()
    })

@app.route('/load/cpu')
def load_cpu():
    """
    Endpoint to generate CPU load
    Starts a background thread that continuously performs CPU-intensive calculations
    """
    # Start CPU intensive task in a background thread
    thread = threading.Thread(target=cpu_intensive_task)
    thread.daemon = True  # Thread will exit when main program exits
    thread.start()
    return jsonify({"message": "CPU load started"})

@app.route('/load/memory')
def load_memory():
    """
    Endpoint to generate memory load
    Starts a background thread that continuously allocates memory
    """
    # Start memory intensive task in a background thread
    thread = threading.Thread(target=memory_intensive_task)
    thread.daemon = True
    thread.start()
    return jsonify({"message": "Memory load started"})

@app.route('/load/http')
def load_http():
    """
    Endpoint to simulate HTTP request load
    Adds 500 requests to the queue and increments the Prometheus counter
    """
    # Simulate HTTP request load - adding 500 requests total
    for _ in range(500):  # Generate 500 requests
        request_queue.put(1)  # Add request to queue
        http_requests_total.inc()  # Increment Prometheus counter
    return jsonify({"message": "500 HTTP requests queued"})

def cpu_intensive_task():
    """
    Function that generates CPU load
    Continuously performs mathematical calculations
    """
    while True:
        # Simulate CPU load by performing calculations
        [i * i for i in range(10000)]

def memory_intensive_task():
    """
    Function that generates memory load
    Continuously allocates memory in 50MB chunks
    """
    # Simulate memory load
    large_list = []
    while True:
        # Allocate 50MB at a time
        large_list.append([0] * (50 * 1024 * 1024))
        time.sleep(0.1)  # Small delay to prevent system lockup

if __name__ == '__main__':
    # Start Prometheus metrics server on port 8000
    start_http_server(8000)
    
    # Run Flask app
    app.run(host='0.0.0.0', port=80) 