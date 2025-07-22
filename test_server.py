#!/usr/bin/env python3
"""
Simple test server to check what's running on port 5000
"""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({"message": "Test server is running!", "status": "success"})

@app.route('/test')
def test():
    return jsonify({"message": "Test route working!", "status": "success"})

if __name__ == '__main__':
    print("Starting test server on port 5000...")
    app.run(debug=True, host='0.0.0.0', port=5000) 