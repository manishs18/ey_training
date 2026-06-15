from nltk.translate.bleu_score import sentence_bleu
from rouge_score import rouge_scorer

scorer = rouge_scorer.RougeScorer(
    ['rougeL'],
    use_stemmer=True
)

def calculate_metrics(df):

    bleu_scores = []
    rouge_scores = []

    for _, row in df.iterrows():
        ground_truth = row["ground_truth"]
        answer = row["answer"]

        if isinstance(ground_truth, list):
            ground_truth = " ".join(str(item) for item in ground_truth)
        else:
            ground_truth = str(ground_truth)

        if isinstance(answer, list):
            answer = " ".join(str(item) for item in answer)
        else:
            answer = str(answer)

        bleu = sentence_bleu(
            [ground_truth.split()],
            answer.split()
        )

        rouge = scorer.score(
            ground_truth,
            answer
        )["rougeL"].fmeasure

        bleu_scores.append(bleu)
        rouge_scores.append(rouge)

    df["bleu"] = bleu_scores
    df["rougeL"] = rouge_scores

    return df