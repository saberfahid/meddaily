import requests
import json

def get_updates():
    token = "8574102270:AAF_Lyi4-oLbx6isrGEPmvBSuHTPNBI56NQ"
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    
    print("Fetching updates for the bot...")
    try:
        response = requests.get(url)
        data = response.json()
        print(json.dumps(data, indent=2))
        
        if data.get("ok") and data.get("result"):
            for update in data["result"]:
                if "message" in update:
                    chat = update["message"]["chat"]
                    print(f"\nFound Chat!")
                    print(f"Title: {chat.get('title')}")
                    print(f"ID: {chat.get('id')}")
                    print(f"Type: {chat.get('type')}")
                elif "my_chat_member" in update:
                    chat = update["my_chat_member"]["chat"]
                    print(f"\nFound Chat from Membership Change!")
                    print(f"Title: {chat.get('title')}")
                    print(f"ID: {chat.get('id')}")
                    print(f"Type: {chat.get('type')}")
        else:
            print("\nNo recent activity found. Please send a message in the group or add the bot to the group now.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_updates()
