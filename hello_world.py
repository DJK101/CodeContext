import json
from flask import Flask
import logging
import os

app = Flask(__name__)

# Configuration and Logging Initialization
def init_config_logging():
    # Set up logging configuration
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=log_level, format="%(asctime)s - %(levelname)s - %(message)s")
    logging.info("Configuration and logging initialized")

# Entry point
def create_app():
    init_config_logging()  # Initialize config and logging
    register_routes(app)    # Register routes
    logging.info("Application setup complete")
    return app

def load_config():
    # Load configuration from config.json
    try:
        with open("config.json") as config_file:
            config = json.load(config_file)
        logging.info("Configuration loaded from config.json")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error("Error loading config.json: %s", e)
        config = {}
    return config

# Register a "hello" handler
def register_routes(app):
    @app.route("/hello")
    def hello():
        logging.info("Hello handler invoked")
        return "Hello World!", 200

# Only run if script is executed directly (for in-process testing)
if __name__ == "__main__":
    config = load_config()
    port = config.get("port", 5000)
    create_app()
    app.run(host="0.0.0.0", port=port)
