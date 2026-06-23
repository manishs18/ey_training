"""
redis_utils.py

Features
---------
✓ RedisMemory class
✓ Works with fakeredis or real Redis/Upstash
✓ Conversation history
✓ Rolling history limit
✓ TTL support
✓ remember_fact()
✓ recall_fact()
✓ forget_fact()
✓ all_facts()
"""

import json
from typing import Optional


class RedisMemory:

    def __init__(

        self,

        redis_client,

        session_id: str,

        history_limit: int = 20,

    ):

        self.redis = redis_client

        self.session_id = session_id

        self.history_limit = history_limit

        self.history_key = f"history:{session_id}"

        self.fact_key = f"facts:{session_id}"

    # =====================================================
    # HISTORY
    # =====================================================

    def append_turn(

        self,

        role: str,

        content,

    ):

        message = {

            "role": role,

            "content": content,

        }

        self.redis.rpush(

            self.history_key,

            json.dumps(message),

        )

        self.redis.ltrim(

            self.history_key,

            -self.history_limit,

            -1,

        )

    def load_history(self):

        history = []

        items = self.redis.lrange(

            self.history_key,

            0,

            -1,

        )

        for item in items:

            if isinstance(item, bytes):

                item = item.decode()

            history.append(

                json.loads(item)

            )

        return history

    def clear_history(self):

        self.redis.delete(

            self.history_key

        )

    def history_size(self):

        return self.redis.llen(

            self.history_key

        )

    # =====================================================
    # FACT MEMORY
    # =====================================================

    def remember_fact(

        self,

        key: str,

        value: str,

        ttl_seconds: Optional[int] = None,

    ):

        """

        Save a fact.

        ttl_seconds=None

        means permanent.

        """

        redis_key = (

            f"{self.fact_key}:{key}"

        )

        self.redis.set(

            redis_key,

            value,

        )

        if ttl_seconds:

            self.redis.expire(

                redis_key,

                ttl_seconds,

            )

        return {

            "success": True,

            "key": key,

            "value": value,

            "ttl": ttl_seconds,

        }

    def recall_fact(

        self,

        key: str,

    ):

        redis_key = (

            f"{self.fact_key}:{key}"

        )

        value = self.redis.get(

            redis_key

        )

        if value is None:

            return None

        if isinstance(value, bytes):

            value = value.decode()

        return value

    def forget_fact(

        self,

        key: str,

    ):

        redis_key = (

            f"{self.fact_key}:{key}"

        )

        deleted = self.redis.delete(

            redis_key

        )

        return {

            "success": bool(deleted),

            "deleted": key,

        }

    def all_facts(self):

        """

        Return every stored fact.

        """

        pattern = (

            f"{self.fact_key}:*"

        )

        keys = self.redis.keys(

            pattern

        )

        facts = {}

        for key in keys:

            redis_key = key

            display_key = key

            if isinstance(key, bytes):

                redis_key = key

                display_key = key.decode()

            value = self.redis.get(

                redis_key

            )

            if isinstance(value, bytes):

                value = value.decode()

            short_name = (

                display_key.split(":")

                [-1]

            )

            facts[short_name] = value

        return facts

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self):

        return {

            "session": self.session_id,

            "history_turns": self.history_size(),

            "facts": len(

                self.all_facts()

            ),

        }


# =========================================================
# LOCAL TEST
# =========================================================

if __name__ == "__main__":

    import fakeredis
    import time

    redis_client = fakeredis.FakeStrictRedis()

    memory = RedisMemory(

        redis_client,

        session_id="demo",

        history_limit=5,

    )

    print()

    print("History Demo")

    print("----------------------")

    memory.append_turn(

        "user",

        "Hello",

    )

    memory.append_turn(

        "assistant",

        "Hi",

    )

    print(

        memory.load_history()

    )

    print()

    print("TTL Demo")

    print("----------------------")

    memory.remember_fact(

        "city",

        "Bangalore",

        ttl_seconds=3,

    )

    print(

        memory.recall_fact(

            "city"

        )

    )

    time.sleep(4)

    print(

        memory.recall_fact(

            "city"

        )

    )

    print()

    print("Remember Demo")

    print("----------------------")

    memory.remember_fact(

        "language",

        "Python",

    )

    memory.remember_fact(

        "framework",

        "FastAPI",

    )

    print(

        memory.all_facts()

    )

    print()

    print("Forget Demo")

    print("----------------------")

    print(

        memory.forget_fact(

            "language"

        )

    )

    print(

        memory.all_facts()

    )

    print()

    print("Summary")

    print("----------------------")

    print(

        memory.summary()

    )