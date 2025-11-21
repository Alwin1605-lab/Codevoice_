import requests

url = "http://localhost:8000/speak/"
files = {"text": (None, "print('hello world')")}
response = requests.post(url, files=files)
print(response.status_code)
print(response.text)
