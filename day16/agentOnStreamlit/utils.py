import time
from datetime import datetime


def get_timestamp():
    """Return current timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def measure_execution_time(func):
    """
    Decorator to measure execution time.
    """

    def wrapper(*args, **kwargs):
        start = time.time()

        result = func(*args, **kwargs)

        end = time.time()

        return result, round(end - start, 2)

    return wrapper


def format_plan(plan):
    """
    Convert plan text into a clean list.
    """

    steps = [
        step.strip()
        for step in plan.split("\n")
        if step.strip()
    ]

    return steps


def format_execution_results(results):
    """
    Convert executor results into display text.
    """

    return "\n".join(results)