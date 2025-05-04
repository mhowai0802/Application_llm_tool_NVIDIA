# backend/app.py
from flask import Flask, jsonify
from flask_cors import CORS
import routes

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Register routes
app.register_blueprint(routes.api_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)