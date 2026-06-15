import pandas as pd
import os

from src.evaluate_ragas import run_ragas
from src.calculate_bleu_rouge import calculate_metrics
from src.token_analysis import process_tokens

df = pd.read_csv(
    "data/rag_results.csv"
)

if os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY"):
    try:
        ragas_df = run_ragas(df)
        df = pd.concat(
            [df, ragas_df],
            axis=1
        )
        print("✓ RAGAS evaluation completed")
    except Exception as e:
        print(f"⚠ RAGAS evaluation skipped: {e}")
else:
    print(
        "⚠ RAGAS evaluation skipped: OPENAI_API_KEY and GROQ_API_KEY are both unset"
    )

df = calculate_metrics(df)

df = process_tokens(df)

df.to_csv(
    "data/metrics_output.csv",
    index=False
)

print("✓ Analysis complete. Output saved to data/metrics_output.csv")