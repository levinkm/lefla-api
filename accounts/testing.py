import requests

import json

url = "http://localhost:8000/api/set-password"

payload = json.dumps(
    {
        "uidb64": "NDA",
        "token": "bd4svr-9e4035e4784f9ca28e447c14e673ea45",
        "password": "",
    }
)
headers = {"Content-Type": "application/json"}

response = requests.post(url, headers=headers, data=payload)

print(response.text)
