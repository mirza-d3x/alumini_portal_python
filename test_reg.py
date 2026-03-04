import requests
files = {'id_card': ('test.txt', b'abc')}
data = {'username': 'testuser2', 'password': 'password', 'role': 'ALUMNI'}
res = requests.post('http://127.0.0.1:8000/api/users/register/', data=data, files=files)
print(res.status_code, res.text)
