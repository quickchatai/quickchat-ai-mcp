import requests


class QuickchatClient:
    def __init__(
        self, api_token: str, base_url: str = "https://app.quickchat.ai"
    ) -> None:
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_token}"}

    def _handle_response(self, response: requests.Response) -> dict:
        if response.status_code == 401:
            raise ValueError("Unauthorized. Double-check your API_TOKEN.")
        if not response.ok:
            raise ValueError(f"API error {response.status_code}: {response.text}")
        if response.status_code == 204 or not response.content:
            return {}
        return response.json()

    def get(self, path: str, params: dict | None = None) -> dict:
        response = requests.get(
            url=f"{self.base_url}{path}",
            headers=self.headers,
            params=params,
        )
        return self._handle_response(response)

    def post(self, path: str, json: dict | None = None) -> dict:
        response = requests.post(
            url=f"{self.base_url}{path}",
            headers=self.headers,
            json=json,
        )
        return self._handle_response(response)

    def patch(self, path: str, json: dict | None = None) -> dict:
        response = requests.patch(
            url=f"{self.base_url}{path}",
            headers=self.headers,
            json=json,
        )
        return self._handle_response(response)

    def put(self, path: str, json: dict | None = None) -> dict:
        response = requests.put(
            url=f"{self.base_url}{path}",
            headers=self.headers,
            json=json,
        )
        return self._handle_response(response)

    def delete(self, path: str, json: dict | None = None) -> dict:
        response = requests.delete(
            url=f"{self.base_url}{path}",
            headers=self.headers,
            json=json,
        )
        return self._handle_response(response)
