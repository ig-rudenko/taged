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
        self.max_length = self.model.config.max_position_embeddings - 2
        if use_cuda:
            # if you have a GPU
            self.model.cuda()

    def _vectorize_chunk(self, text: str) -> np.ndarray:
        tokens = self.tokenizer(
            text, padding=True, truncation=True, return_tensors="pt", max_length=self.max_length
        )
        with torch.no_grad():
            model_output = self.model(**{k_: v_.to(self.model.device) for k_, v_ in tokens.items()})
        embeddings = model_output.last_hidden_state[:, 0, :]
        embeddings = torch.nn.functional.normalize(embeddings)
        return embeddings[0].cpu().numpy()

    def vectorize(self, text: str) -> np.ndarray:
        tokens = self.tokenizer.tokenize(text)
        chunks = [
            self.tokenizer.convert_tokens_to_string(tokens[i : i + self.max_length])
            for i in range(0, len(tokens), self.max_length)
        ]

        vectors = []
        weights = []
        for chunk in chunks:
            vector = self._vectorize_chunk(chunk)
            weight = len(chunk.split())  # Вес пропорционален количеству слов в части
            vectors.append(vector)
            weights.append(weight)

        # Взвешенное усреднение
        weights = np.array(weights) / np.sum(weights)
        weighted_vectors = np.average(vectors, axis=0, weights=weights)
        return weighted_vectors
