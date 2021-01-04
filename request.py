import json
import requests
import uuid
from web3 import Web3

URL = 'http://172.17.0.1/'

ADMIN_URL = 'http://172.17.0.1:8000/api/v1/projects/'
data = {
  "manager_id": 5,
  "name": f"TEST {uuid.uuid4()}",
  "max_requests_per_month": 1000
}

res = requests.post(ADMIN_URL, data)

content = res.content
decoded = json.loads(content)


print(res)
print(decoded)

w3 = Web3(Web3.HTTPProvider(URL + decoded['project_id']))
print(w3.eth.block_number())
