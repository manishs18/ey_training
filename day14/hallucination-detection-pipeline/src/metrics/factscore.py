def factscore(answer, reference):
    ans_tokens = set(answer.lower().split())
    ref_tokens = set(reference.lower().split())

    if len(ans_tokens) == 0:
        return 0

    return len(ans_tokens & ref_tokens) / len(ans_tokens)