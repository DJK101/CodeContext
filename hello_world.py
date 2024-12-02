from flask import Flask, jsonify
from flask_caching import Cache
import logging
import json
import datetime
from lib.block_timer import BlockTimer
from lib.data_snapshot import DataSnapshot

app = Flask(__name__)

# Configure caching
app.config["CACHE_TYPE"] = "SimpleCache"  # Use in-memory cache
app.config["CACHE_DEFAULT_TIMEOUT"] = 10  # Default timeout: 300 seconds
cache = Cache(app)

# Global instance of DataSnapshot
data_snapshot = DataSnapshot()


# Load configuration from config.json
def load_config():
    try:
        with open("config.json") as config_file:
            config = json.load(config_file)
        logging.info("Configuration loaded from config.json")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error("Error loading config.json: %s", e)
        config = {}
    return config


# Basic setup for logging
def init_config_logging():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.info("Configuration and logging initialized")


# Endpoint for /hello
@app.route("/hello")
def hello():
    with BlockTimer("Hello Handler Timer") as timer:
        # This is where you would handle the request logic
        response = "Hello World!"
    # Record metrics for this request
    data_snapshot.record_request(timer.elapsed)
    return response, 200


# New /metrics handler
@app.route("/metrics")
def metrics():
    """Return metrics in JSON format."""
    return jsonify(data_snapshot.get_metrics())


@app.route("/test")
def test():
    cache_key = "system_metrics"

    if (result := cache.get(cache_key)) is None:
        result = data_snapshot.gather_system_metrics().__dict__
        cache.set(cache_key, result, timeout=10)

    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "status": "success",
        "content": result,
    }


if __name__ == "__main__":
    init_config_logging()
    config = load_config()
    port = config.get("port", 5000)
    app.run(host="0.0.0.0", port=port)
