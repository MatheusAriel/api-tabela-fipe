import requests
from enum import Enum


class Methods(Enum):
    POST = 'post'
    GET = 'get'
    PUT = 'put'
    DELETE = 'delete'
    PATCH = 'patch'


class APIError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return f"Erro {self.status_code}: {self.message}"


class APIClient:
    def __init__(self, base_url, time_out=30, headers=None):
        self.base_url = base_url
        self.time_out = time_out
        self.headers = headers or {"Content-Type": "application/json"}

    def request(self, endpoint, method=Methods.GET.value, json=None):
        url = f"{self.base_url}/{endpoint}"
        try:
            if method == 'get':
                response = requests.get(url, headers=self.headers, timeout=self.time_out)
            elif method == 'post':
                response = requests.post(url, json=json, headers=self.headers, timeout=self.time_out)
            elif method == 'put':
                response = requests.put(url, json=json, headers=self.headers, timeout=self.time_out)
            elif method == 'put':
                response = requests.delete(url, json=json, headers=self.headers, timeout=self.time_out)
            elif method == 'patch':
                response = requests.patch(url, json=json, headers=self.headers, timeout=self.time_out)
            else:
                raise ValueError("Método inválido.")

            if response.status_code != 200:
                raise APIError(response.status_code, response.json().get("message", "Erro desconhecido."))

            result = response.json()
            if 'erro' in response:
                raise APIError(response.status_code, result['erro'])

            return result

        except (requests.exceptions.RequestException, Exception) as error:
            raise APIError(0, f"Erro ({endpoint}): {error}")
