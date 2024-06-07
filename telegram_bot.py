import requests
from flask import Flask, request

app = Flask(__name__)
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

@app.route(f'/{TOKEN}', methods=['POST'])
def respond():
    data = request.json
    chat_id = data['message']['chat']['id']
    message = data['message']['text']
    
    if message == "/status":
        response = requests.get("http://catalog-service:5003/catalog/vehicles")
        reply = response.json()
        requests.post(f'https://api.telegram.org/bot{TOKEN}/sendMessage', data={'chat_id': chat_id, 'text': str(reply)})

    return "ok"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5004)
