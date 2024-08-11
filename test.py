import requests

resp = requests.request("GET", "http://127.0.0.1/")
print(resp.reason)
