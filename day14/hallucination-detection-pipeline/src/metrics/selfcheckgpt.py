from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import numpy as np

generator = pipeline("text-generation", model="gpt2")
model = SentenceTransformer('all-MiniLM-L6-v2')

def selfcheckgpt(question, n=3):
    outputs = []

    for _ in range(n):
        res = generator(question, max_length=60, do_sample=True)[0]["generated_text"]
        outputs.append(res)

    emb = model.encode(outputs)

    sims = []
    for i in range(len(outputs)):
        for j in range(i+1, len(outputs)):
            sims.append(util.cos_sim(emb[i], emb[j]).item())

    return np.mean(sims)