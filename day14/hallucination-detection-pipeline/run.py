import sys
import os

sys.path.append(os.path.abspath("."))

from src.pipeline.data_loader import load_data
from src.pipeline.run_evaluation import run

df = load_data("data/sample_inputs.csv")

results = run(df)

print(results)

results.to_csv("outputs/metrics_results.csv", index=False)