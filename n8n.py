import requests
requests.post("http://localhost:5678/webhook-test/test", json={"message": "Hello, n8n!"})