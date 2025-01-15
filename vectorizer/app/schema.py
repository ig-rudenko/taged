from pydantic import BaseModel


class TokenizerRequest(BaseModel):
    text: str


class TokenizerResponse(BaseModel):
    vector: list[float]
