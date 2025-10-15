# /api/fill-d5.py
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.get("/")
def ping():
    return "ok", 200

@app.post("/")
def fill():
    data = request.get_json(silent=True)
    return jsonify(received=bool(data)), 200