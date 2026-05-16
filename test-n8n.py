import requests

url = "http://localhost:5678/webhook-test/test"

data = {
    "text": "vacation request"
}

res = requests.post(url, json=data)

print(res.text)