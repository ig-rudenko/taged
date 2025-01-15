from pydantic_settings import BaseSettings


class _Settings(BaseSettings):
    model_name: str = "cointegrated/rubert-tiny"
    tokenizer_name: str = "cointegrated/rubert-tiny"
    use_cuda: bool = False


settings = _Settings()
