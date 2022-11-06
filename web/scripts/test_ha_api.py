from requests import get

supervisor_token = '4b3d8638ca41c3aef50c1267b3a588e2452b4e75b4e57de1bd10455a6c160900cd004d41c72b3d54e21b852574a559e19a0c1413b20612a4b'

url = "http://supervisor/core/api"
headers = {
    "Authorization": f"Bearer {supervisor_token}",
    "content-type": "application/json",
}

response = get(url, headers=headers)
print(response.text)