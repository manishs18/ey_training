# Day 11 Fintech NLP Prototype Workflow

This file explains the project in step-by-step form with folder structure, code flow, and the reason each module exists.

## What this project does

The project has three NLP tasks:

- classify support tickets
- summarize earnings snippets
- answer questions from a policy PDF

It uses Groq when available, but also falls back to local deterministic logic so the project still runs without an API key.

## Folder structure

```text
fintech_nlp_prototype/
  config.py
  data/
    tickets.csv
    earnings_snippets/
      snippets.txt
    policy_docs/
      Day4_coding_Assignment.pdf
  outputs/
    ticket_eval.csv
    summaries.csv
    qa_answers.csv
  src/
    __init__.py
    eval.py
    groq_utils.py
    main.py
    qa_bot.py
    summarizer.py
    ticket_classifier.py
    utils.py
  requirements.txt
  README.md
```

## Why these files are used

- `main.py` is the orchestration layer. It runs all three tasks in sequence.
- `ticket_classifier.py` contains the ticket classification logic and SLA mapping.
- `summarizer.py` turns earnings snippets into short summaries.
- `qa_bot.py` builds the PDF question-answering chain.
- `groq_utils.py` handles Groq setup and JSON parsing.
- `eval.py` saves results and computes ticket classification accuracy.
- `utils.py` contains reusable helper functions for text processing.
- `config.py` stores the Groq settings in one place.

## Step-by-step workflow

1. `main.py` adds `src/` to the import path and creates the `outputs/` folder.
2. It loads `tickets.csv` from `data/`.
3. Each ticket is passed to `classify_ticket()`.
4. The classifier first tries Groq-based JSON classification.
5. If Groq is unavailable or fails, the code falls back to a rule-based classifier.
6. `save_ticket_eval()` writes ticket predictions to `outputs/ticket_eval.csv` and prints accuracy.
7. It loads earnings snippets from `data/earnings_snippets/snippets.txt`.
8. `summarize()` generates short summaries using Groq or a local fallback.
9. The snippet and summary pairs are saved to `outputs/summaries.csv`.
10. `build_qa_chain()` reads the policy PDF, extracts text, chunks it, and creates a QA chain.
11. Two sample questions are asked against the policy document.
12. The answers are saved to `outputs/qa_answers.csv`.

## Workflow diagram

```mermaid
flowchart TD
    A[data/tickets.csv] --> B[classify_ticket()]
    B --> C[Groq JSON classification]
    B --> D[Rule-based fallback]
    C --> E[save_ticket_eval()]
    D --> E
    E --> F[outputs/ticket_eval.csv]

    G[data/earnings_snippets/snippets.txt] --> H[summarize()]
    H --> I[outputs/summaries.csv]

    J[data/policy_docs/Day4_coding_Assignment.pdf] --> K[build_qa_chain()]
    K --> L[Ask questions]
    L --> M[outputs/qa_answers.csv]
```

## Why this design is useful

- The project is split into small modules so each NLP task is easy to test and replace.
- The Groq wrapper keeps API access separate from business logic.
- Fallback logic is important because it lets the project run even when the API key is missing.
- Saving outputs to CSV makes the results easy to review in Excel or pandas.
- The QA chain uses chunking because long PDF text cannot be sent or searched as one giant block reliably.

## Code flow by module

### `main.py`

- Loads input data
- calls the classifier
- runs the summarizer
- builds the QA chain
- saves all outputs

### `ticket_classifier.py`

- tries Groq first
- parses JSON response
- assigns SLA hours based on the label
- falls back to keyword rules when needed

### `summarizer.py`

- uses a prompt for each earnings snippet
- switches between zero-shot and few-shot style prompts
- uses a local first-sentence fallback if Groq fails

### `qa_bot.py`

- extracts text from the PDF
- splits the text into chunks
- picks the best matching chunk for a question
- optionally uses Groq to turn the chunk into a better answer

## Important insight

This project is more than just prompt calls. It is a small production-style NLP workflow with:

- input loading
- prompt-based reasoning
- deterministic fallback behavior
- evaluation
- structured output files

That makes it useful for learning how to combine LLM behavior with safer local logic.