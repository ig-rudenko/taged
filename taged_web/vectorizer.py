import requests
from django.conf import settings


def vectorize(text: str) -> list[float]:
    resp = requests.post(f"{settings.VECTORIZE_URL}/api/v1/vectorize", json={"text": text})
    if resp.status_code == 200:
        data = resp.json()
        return data["vector"]
    else:
        return []
