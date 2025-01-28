from fastapi import APIRouter

from .schema import TokenizerRequest, TokenizerResponse
from .vectorizer import Vectorizer

router = APIRouter()


@router.post("/vectorize", response_model=TokenizerResponse)
def vectorize(data: TokenizerRequest):
    vectorizer = Vectorizer()
    print("Text: ", data.text[:50])
    vector = vectorizer.vectorize(data.text)
    print("Vector: ", vector[:10])
    return {"vector": vector}
