from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/logistics/door', methods=['POST'])
def control_door():
    data = request.json
    # Simulate door control logic
    return jsonify({"status": "door action performed"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
