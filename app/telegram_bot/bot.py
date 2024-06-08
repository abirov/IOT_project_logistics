import requests
import time
import json
from pymongo import MongoClient

API_TOKEN = 'YOUR_TELEGRAM_BOT_API_TOKEN'
CHAT_ID = 'YOUR_CHAT_ID'
BASE_URL = f'https://api.telegram.org/bot{API_TOKEN}/sendMessage'

client = MongoClient('localhost', 27017)
db = client['logistics_db']
logistics_points_collection = db['logistics_points']

def send_notification(message):
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    requests.post(BASE_URL, data=payload)

def check_delivery_status():
    points = list(logistics_points_collection.find())
    for point in points:
        if point['status'] == 'Delivered':
            send_notification(f"Package delivered to {point['address']}")

if __name__ == '__main__':
    while True:
        check_delivery_status()
        time.sleep(60)  # Check every minute
