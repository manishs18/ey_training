import time


class Reviewer:

    def run(self, article):

        time.sleep(1)

        return f"""
==============================

FINAL OUTPUT

{article}

Approved by Reviewer

==============================
"""