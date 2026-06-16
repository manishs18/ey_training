from bert_score import score

def compute_bertscore(cands, refs):
    P, R, F1 = score(cands, refs, lang="en")
    return F1.numpy()