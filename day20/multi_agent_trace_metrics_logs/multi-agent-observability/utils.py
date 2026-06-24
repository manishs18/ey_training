import uuid
from datetime import datetime


def generate_run_id():
    return str(uuid.uuid4())


def timestamp():
    return datetime.now().isoformat(timespec="seconds")