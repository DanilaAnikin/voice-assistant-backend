import requests

# Load your cookies.json file
import json
with open("cookies.json", "r") as f:
    cookies = json.load(f)

# Convert cookies into a request header
cookie_str = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
headers = {"Cookie": cookie_str}

# Send a request to Bing's API
response = requests.get("https://edgeservices.bing.com/edgesvc/turing/conversation/create", headers=headers)

# Print status and response
print("Status Code:", response.status_code)
print("Response:", response.text)
