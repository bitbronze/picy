import requests

resp = requests.request("SOURCE", "http://127.0.0.1/")
print(resp.reason)
