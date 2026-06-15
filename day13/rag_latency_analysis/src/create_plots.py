import matplotlib.pyplot as plt
import seaborn as sns

def plot_context_precision(df):

    plt.figure(figsize=(8,5))

    sns.scatterplot(
        data=df,
        x="context_precision",
        y="latency_ms"
    )

    plt.savefig(
        "plots/latency_vs_context_precision.png"
    )

def plot_faithfulness(df):

    plt.figure(figsize=(8,5))

    sns.scatterplot(
        data=df,
        x="faithfulness",
        y="latency_ms"
    )

    plt.savefig(
        "plots/latency_vs_faithfulness.png"
    )


def plot_answer_relevance(df):

    plt.figure(figsize=(8,5))

    sns.scatterplot(
        data=df,
        x="answer_relevancy",
        y="latency_ms"
    )

    plt.savefig(
        "plots/latency_vs_answer_relevance.png"
    )


def plot_bleu(df):

    sns.scatterplot(
        data=df,
        x="bleu",
        y="latency_ms"
    )

    plt.savefig(
        "plots/latency_vs_bleu.png"
    )


def plot_rouge(df):

    sns.scatterplot(
        data=df,
        x="rougeL",
        y="latency_ms"
    )

    plt.savefig(
        "plots/latency_vs_rouge.png"
    )


def plot_tokens(df):

    sns.regplot(
        data=df,
        x="total_tokens",
        y="latency_ms"
    )

    plt.savefig(
        "plots/latency_vs_tokens.png"
    )


def bubble_plot(df):

    plt.figure(figsize=(10,7))

    scatter = plt.scatter(
        df["context_precision"],
        df["faithfulness"],
        s=df["latency_ms"]/10,
        c=df["answer_relevancy"],
        cmap="viridis"
    )

    plt.colorbar(scatter)

    plt.savefig(
        "plots/bubble_analysis.png"
    )