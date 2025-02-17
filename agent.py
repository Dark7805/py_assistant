import requests
print(requests.get("https://httpbin.org/user-agent").json())