# Day19 Agentic AI + FastAPI + Redis Memory

## Project Structure

```
day19_agent/
│
├── app.py
├── api.py
├── redis_utils.py
├── tools.py
├── requirements.txt
├── .env.example
├── README.md
└── .vscode/
    └── launch.json
```

---

## Features

- Anthropic Claude Tool Use
- FastAPI Backend
- Redis Memory
- Rolling Summary
- TTL Support
- Forget Tool
- Parallel Tool Calls
- PII Guard
- Token Accounting
- Real Redis / Upstash Compatible

---

## Installation

### 1. Create Virtual Environment

Windows

```bash
python -m venv .venv
```

Activate

```bash
.venv\Scripts\activate
```

---

### 2. Install Packages

```bash
pip install -r requirements.txt
```

---

### 3. Configure Environment

Copy

```
.env.example
```

to

```
.env
```

Update

```
ANTHROPIC_API_KEY
```

---

### 4. Start Redis

Local Docker

```bash
docker run -p 6379:6379 redis
```

or use Upstash

```
REDIS_URL=redis://default:password@hostname:6379
```

---

### 5. Start FastAPI

```bash
python api.py
```

Open

```
http://localhost:8000/docs
```

---

### 6. Run Agent

```bash
python app.py
```

---

## Assignment Tasks Covered

### 1. Rolling Summary

Conversation history is compacted when it exceeds the configured limit.

### 2. TTL + Forget Tool

```python
remember_fact(
    key="city",
    value="Bangalore",
    ttl_seconds=30
)

forget_fact("city")
```

### 3. Parallel Lookups

Claude can call

- get_order()
- get_customer()

within a single turn.

### 4. PII Protection

Rejects

- Email addresses
- Credit card numbers

Example

```
abc@gmail.com
4111111111111111
```

### 5. Token Accounting

Displays

```
Input Tokens
Output Tokens
```

for every interaction.

### 6. Real Redis

Supports

```
redis.Redis.from_url(REDIS_URL)
```

without changing RedisMemory.

---

## Run Individual Files

```
python redis_utils.py
python tools.py
python api.py
python app.py
```

---

## Tech Stack

- Python 3.12+
- Anthropic SDK
- FastAPI
- Redis
- httpx
- Pydantic
- Uvicorn
