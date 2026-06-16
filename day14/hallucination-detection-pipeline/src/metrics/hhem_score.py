from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def hhem_score(answer, reference):
    emb_a = model.encode(answer, convert_to_tensor=True)
    emb_r = model.encode(reference, convert_to_tensor=True)

    similarity = util.pytorch_cos_sim(emb_a, emb_r).item()
    return 1 - similarity   # hallucination risk