import requests
import os

def test_telegram():
    token = "8574102270:AAF_Lyi4-oLbx6isrGEPmvBSuHTPNBI56NQ"
    chat_id = "@MedDaily_ai" # User provided this in .env
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "Hello! This is a test from the Medical Education App."
    }
    
    print(f"Testing Telegram with chat_id: {chat_id}")
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_telegram()
