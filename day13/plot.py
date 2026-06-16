import pandas as pd
import matplotlib.pyplot as plt

# Example structure (replace with your actual values)
df = pd.DataFrame({
    "Query": ["Q1","Q2","Q3","Q4","Q5","Q6","Q7","Q8"],
    "Latency": [0,0,0,0,0,0,0,0],
    "Total_Tokens": [0,0,0,0,0,0,0,0],
    "Context_Precision": [0,0,0,0,0,0,0,0],
    "Answer_Relevance": [0,0,0,0,0,0,0,0]
})

fig, ax = plt.subplots(2, 2, figsize=(12,8))

# Latency
ax[0,0].plot(df["Query"], df["Latency"], marker='o')
ax[0,0].set_title("Latency per Query")

# Tokens
ax[0,1].plot(df["Query"], df["Total_Tokens"], marker='o', color='orange')
ax[0,1].set_title("Total Tokens")

# Context Precision
ax[1,0].plot(df["Query"], df["Context_Precision"], marker='o', color='green')
ax[1,0].set_title("Context Precision")

# Answer Relevance
ax[1,1].plot(df["Query"], df["Answer_Relevance"], marker='o', color='red')
ax[1,1].set_title("Answer Relevance")

plt.tight_layout()
plt.show()