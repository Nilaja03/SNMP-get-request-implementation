from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Server is running ✅"

@app.route('/test')
def test():
    return jsonify({"message": "SNMP route working"})
