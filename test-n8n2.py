import requests
res= requests.post(
    "http://localhost:5678/webhook-test/test",
    json={"text": "hello"}
)
print(res.text)