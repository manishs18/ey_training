"""
tools.py

Tool implementations for the Anthropic agent.

Features
--------
✓ get_order()
✓ get_customer()
✓ remember_fact()
✓ recall_fact()
✓ forget_fact()
✓ PII protection
✓ Tool dispatcher
✓ Anthropic tool schemas
"""

import re
import httpx

# ==========================================================
# PII REGEX
# ==========================================================

EMAIL_REGEX = re.compile(

    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

)

CARD_REGEX = re.compile(

    r"\b(?:\d[ -]*?){13,16}\b"

)

# ==========================================================
# API CLIENT
# ==========================================================

BASE_URL = "http://localhost:8000"

client = httpx.Client(

    base_url=BASE_URL,

    timeout=10.0,

)

memory = None


def set_memory(memory_instance):

    """
    Inject RedisMemory instance from app.py
    """

    global memory

    memory = memory_instance


# ==========================================================
# ORDER TOOL
# ==========================================================

def get_order(order_id: str):

    response = client.get(

        f"/orders/{order_id}"

    )

    if response.status_code != 200:

        return {

            "error": "Order not found"

        }

    return response.json()


# ==========================================================
# CUSTOMER TOOL
# ==========================================================

def get_customer(customer_id: str):

    response = client.get(

        f"/customers/{customer_id}"

    )

    if response.status_code != 200:

        return {

            "error": "Customer not found"

        }

    return response.json()


# ==========================================================
# MEMORY TOOLS
# ==========================================================

def remember_fact(

    key,

    value,

    ttl_seconds=300,

):

    if EMAIL_REGEX.search(value):

        return {

            "is_error": True,

            "message": "Email addresses cannot be stored."

        }

    if CARD_REGEX.search(value):

        return {

            "is_error": True,

            "message": "Card numbers cannot be stored."

        }

    return memory.remember_fact(

        key,

        value,

        ttl_seconds,

    )


def recall_fact(

    key,

):

    value = memory.recall_fact(

        key

    )

    return {

        "key": key,

        "value": value,

    }


def forget_fact(

    key,

):

    return memory.forget_fact(

        key

    )


# ==========================================================
# TOOL DISPATCHER
# ==========================================================

TOOL_MAP = {

    "get_order": get_order,

    "get_customer": get_customer,

    "remember_fact": remember_fact,

    "recall_fact": recall_fact,

    "forget_fact": forget_fact,

}


def run_tool(

    tool_name,

    tool_input,

):

    tool = TOOL_MAP.get(

        tool_name

    )

    if tool is None:

        return (

            {

                "error": "Unknown tool"

            },

            True,

        )

    try:

        result = tool(

            **tool_input

        )

        is_error = False

        if isinstance(

            result,

            dict,

        ):

            if result.get(

                "is_error"

            ):

                is_error = True

            if "error" in result:

                is_error = True

        return (

            result,

            is_error,

        )

    except Exception as e:

        return (

            {

                "error": str(e)

            },

            True,

        )


# ==========================================================
# ANTHROPIC TOOL SCHEMAS
# ==========================================================

TOOL_SCHEMAS = [

    {

        "name": "get_order",

        "description": "Lookup an order using order id.",

        "input_schema": {

            "type": "object",

            "properties": {

                "order_id": {

                    "type": "string"

                }

            },

            "required": [

                "order_id"

            ],

        },

    },

    {

        "name": "get_customer",

        "description": "Lookup a customer using customer id.",

        "input_schema": {

            "type": "object",

            "properties": {

                "customer_id": {

                    "type": "string"

                }

            },

            "required": [

                "customer_id"

            ],

        },

    },

    {

        "name": "remember_fact",

        "description": "Remember a user preference or fact with optional TTL.",

        "input_schema": {

            "type": "object",

            "properties": {

                "key": {

                    "type": "string"

                },

                "value": {

                    "type": "string"

                },

                "ttl_seconds": {

                    "type": "integer"

                },

            },

            "required": [

                "key",

                "value"

            ],

        },

    },

    {

        "name": "recall_fact",

        "description": "Recall a previously remembered fact.",

        "input_schema": {

            "type": "object",

            "properties": {

                "key": {

                    "type": "string"

                }

            },

            "required": [

                "key"

            ],

        },

    },

    {

        "name": "forget_fact",

        "description": "Delete a stored fact.",

        "input_schema": {

            "type": "object",

            "properties": {

                "key": {

                    "type": "string"

                }

            },

            "required": [

                "key"

            ],

        },

    },

]

# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    print(

        TOOL_MAP.keys()

    )