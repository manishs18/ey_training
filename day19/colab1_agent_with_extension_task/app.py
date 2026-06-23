import os
import re
import json
import redis
import httpx
from dotenv import load_dotenv
from anthropic import Anthropic

from redis_utils import RedisMemory
from tools import (
    TOOL_SCHEMAS,
    run_tool,
)

load_dotenv()

# ==============================================
# CONFIG
# ==============================================

API_KEY = os.getenv("ANTHROPIC_API_KEY")

MODEL = "claude-3-5-sonnet-latest"

REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0",
)

BASE_URL = os.getenv(
    "BASE_URL",
    "http://localhost:8000",
)

MAX_HISTORY = 20

client_ai = Anthropic(
    api_key=API_KEY
)

redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
)

http_client = httpx.Client(
    base_url=BASE_URL
)

memory = RedisMemory(

    redis_client,

    session_id="demo-user",

    history_limit=MAX_HISTORY,

)

SYSTEM_PROMPT = """

You are an AI order support assistant.

Always use tools whenever external data is required.

Available capabilities

1.

Get order

2.

Get customer

3.

Remember facts

4.

Recall facts

5.

Forget facts

Never hallucinate.

"""


# ==============================================
# TOKEN ACCOUNTING
# ==============================================

TOTAL_INPUT = 0

TOTAL_OUTPUT = 0


def update_usage(resp):

    global TOTAL_INPUT

    global TOTAL_OUTPUT

    if hasattr(resp, "usage"):

        TOTAL_INPUT += resp.usage.input_tokens

        TOTAL_OUTPUT += resp.usage.output_tokens

        print()

        print("Input Tokens :", TOTAL_INPUT)

        print("Output Tokens:", TOTAL_OUTPUT)

        print()


# ==============================================
# HISTORY COMPACTION
# ==============================================


def compact_history():

    history = memory.load_history()

    if len(history) <= MAX_HISTORY:

        return

    oldest = history[:10]

    summary_text = ""

    for item in oldest:

        summary_text += (

            item["role"]

            + ": "

            + str(item["content"])

            + "\n"

        )

    response = client_ai.messages.create(

        model=MODEL,

        max_tokens=200,

        messages=[

            {

                "role": "user",

                "content":

                "Summarize the following conversation:\n"

                + summary_text,

            }

        ],

    )

    summary = ""

    for block in response.content:

        if block.type == "text":

            summary += block.text

    redis_client.delete(

        memory.history_key

    )

    memory.append_turn(

        "assistant",

        "SUMMARY\n\n" + summary,

    )

    for item in history[10:]:

        memory.append_turn(

            item["role"],

            item["content"],

        )


# ==============================================
# AGENT LOOP
# ==============================================


def agent_turn(

    user_message,

    verbose=True,

    max_steps=8,

):

    compact_history()

    memory.append_turn(

        "user",

        user_message,

    )

    messages = memory.load_history()

    for step in range(max_steps):

        response = client_ai.messages.create(

            model=MODEL,

            max_tokens=1024,

            system=SYSTEM_PROMPT,

            tools=TOOL_SCHEMAS,

            messages=messages,

        )

        update_usage(response)

        if response.stop_reason == "tool_use":

            assistant_blocks = []

            for block in response.content:

                assistant_blocks.append(

                    block.model_dump()

                )

            messages.append(

                {

                    "role": "assistant",

                    "content": assistant_blocks,

                }

            )

            tool_results = []

            # Parallel tool execution

            for block in response.content:

                if block.type != "tool_use":

                    continue

                if verbose:

                    print()

                    print(

                        "Running:",

                        block.name,

                    )

                    print(

                        block.input,

                    )

                    print()

                output, is_error = run_tool(

                    block.name,

                    block.input,

                )

                tool_results.append(

                    {

                        "type": "tool_result",

                        "tool_use_id": block.id,

                        "content": json.dumps(

                            output

                        ),

                        "is_error": is_error,

                    }

                )

            messages.append(

                {

                    "role": "user",

                    "content": tool_results,

                }

            )

            continue

        final_answer = ""

        for block in response.content:

            if block.type == "text":

                final_answer += block.text

        memory.append_turn(

            "assistant",

            final_answer,

        )

        return final_answer

    return "Maximum steps reached."

# ============================================================
# DEMO FUNCTIONS
# ============================================================

def demo_order_lookup():

    print("\n==============================")
    print("ORDER LOOKUP")
    print("==============================")

    print(

        agent_turn(

            "What is the status of order A1001?"

        )

    )


def demo_customer_lookup():

    print("\n==============================")
    print("CUSTOMER LOOKUP")
    print("==============================")

    print(

        agent_turn(

            "Who is customer C1001?"

        )

    )


# ============================================================
# MEMORY DEMO
# ============================================================

def demo_memory():

    print("\n==============================")
    print("MEMORY DEMO")
    print("==============================")

    print(

        agent_turn(

            "Remember that my shipping preference is express."

        )

    )

    print(

        agent_turn(

            "What is my shipping preference?"

        )

    )


# ============================================================
# TTL DEMO
# ============================================================

def demo_ttl():

    print("\n==============================")
    print("TTL DEMO")
    print("==============================")

    output, error = run_tool(

        "remember_fact",

        {

            "key": "budget",

            "value": "500",

            "ttl_seconds": 5,

        },

    )

    print(output)

    print()

    output, error = run_tool(

        "recall_fact",

        {

            "key": "budget"

        },

    )

    print(output)

    import time

    print()

    print("Waiting for expiration...")

    time.sleep(6)

    print()

    output, error = run_tool(

        "recall_fact",

        {

            "key": "budget"

        },

    )

    print(output)


# ============================================================
# FORGET TOOL DEMO
# ============================================================

def demo_forget():

    print("\n==============================")
    print("FORGET TOOL")
    print("==============================")

    run_tool(

        "remember_fact",

        {

            "key": "language",

            "value": "python",

        },

    )

    print(

        run_tool(

            "recall_fact",

            {

                "key": "language"

            },

        )

    )

    print()

    run_tool(

        "forget_fact",

        {

            "key": "language"

        },

    )

    print()

    print(

        run_tool(

            "recall_fact",

            {

                "key": "language"

            },

        )

    )


# ============================================================
# PII PROTECTION DEMO
# ============================================================

def demo_pii():

    print("\n==============================")
    print("PII PROTECTION")
    print("==============================")

    print(

        run_tool(

            "remember_fact",

            {

                "key": "email",

                "value": "abc@gmail.com",

            },

        )

    )

    print()

    print(

        run_tool(

            "remember_fact",

            {

                "key": "card",

                "value": "4111111111111111",

            },

        )

    )

    print()

    print(

        run_tool(

            "remember_fact",

            {

                "key": "city",

                "value": "Bangalore",

            },

        )

    )


# ============================================================
# PARALLEL TOOL DEMO
# ============================================================

def demo_parallel():

    print("\n==============================")
    print("PARALLEL TOOL CALLS")
    print("==============================")

    question = """

    Find customer C1001

    and

    order A1002

    and summarize both.

    """

    answer = agent_turn(

        question

    )

    print(answer)


# ============================================================
# ROLLING SUMMARY DEMO
# ============================================================

def demo_summary():

    print("\n==============================")
    print("ROLLING SUMMARY")
    print("==============================")

    for i in range(25):

        memory.append_turn(

            "user",

            f"Message number {i}",

        )

    compact_history()

    history = memory.load_history()

    print()

    print(

        "History Length:",

        len(history),

    )

    print()

    print(

        history[0],

    )


# ============================================================
# MULTI TURN CHAT
# ============================================================

def chat():

    print()

    print("==============================")

    print("CHAT MODE")

    print("==============================")

    print()

    print("Type quit to exit.")

    print()

    while True:

        message = input("YOU : ")

        if message.lower() == "quit":

            break

        response = agent_turn(

            message

        )

        print()

        print(

            "BOT :", response

        )

        print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print()

    print("=======================================")

    print("DAY19 AGENTIC SYSTEM")

    print("=======================================")

    demo_order_lookup()

    demo_customer_lookup()

    demo_memory()

    demo_ttl()

    demo_forget()

    demo_pii()

    demo_parallel()

    demo_summary()

    print()

    print("=======================================")

    print("TOKEN TOTALS")

    print("=======================================")

    print()

    print(

        "Input Tokens :", TOTAL_INPUT

    )

    print(

        "Output Tokens:", TOTAL_OUTPUT

    )

    print()

    # Uncomment to enable interactive mode

    # chat()