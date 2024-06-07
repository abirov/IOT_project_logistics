from flask import Flask, request, jsonify
import paho.mqtt.publish as publish

app = Flask(__name__)

@app.route('/vehicle/status', methods=['POST'])
def update_status():
    data = request.json
    publish.single("vehicles/status", str(data), hostname="mqtt-broker")
    return jsonify({"status": "updated"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
