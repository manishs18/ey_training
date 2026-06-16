import pandas as pd

from src.metrics.factscore import factscore
from src.metrics.hhem_score import hhem_score
from src.metrics.bertscore_metric import compute_bertscore
from src.metrics.selfcheckgpt import selfcheckgpt
from src.metrics.hallucination_risk import hallucination_risk


def run(df):

    results = []

    bert_scores = compute_bertscore(
        df["generated_answer"].tolist(),
        df["reference"].tolist()
    )

    for i in range(len(df)):

        fact = factscore(df.loc[i, "generated_answer"], df.loc[i, "reference"])
        hhem = hhem_score(df.loc[i, "generated_answer"], df.loc[i, "reference"])
        selfcheck = selfcheckgpt(df.loc[i, "question"])

        bert = bert_scores[i]

        risk = hallucination_risk(fact, hhem, bert, selfcheck)

        results.append({
            "question": df.loc[i, "question"],
            "factscore": fact,
            "hhem": hhem,
            "bertscore": bert,
            "selfcheck": selfcheck,
            "risk": risk
        })

    return pd.DataFrame(results)