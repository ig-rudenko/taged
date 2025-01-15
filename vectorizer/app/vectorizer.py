import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel

from .deco import singleton
from .settings import settings


@singleton
class Vectorizer:

    def __init__(self, use_cuda: bool = False):
        self.tokenizer = AutoTokenizer.from_pretrained(settings.tokenizer_name)
        self.model = AutoModel.from_pretrained(settings.model_name)
        if use_cuda:
            # if you have a GPU
            self.model.cuda()

    def vectorize(self, text: str) -> np.ndarray:
        t = self.tokenizer(text, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            model_output = self.model(**{k_: v_.to(self.model.device) for k_, v_ in t.items()})
        embeddings = model_output.last_hidden_state[:, 0, :]
        embeddings = torch.nn.functional.normalize(embeddings)
        return embeddings[0].cpu().numpy()


if __name__ == "__main__":
    vectorizer = Vectorizer("cointegrated/rubert-tiny", "cointegrated/rubert-tiny")
    v1 = vectorizer.vectorize("привет мир")
    print(v.shape)
