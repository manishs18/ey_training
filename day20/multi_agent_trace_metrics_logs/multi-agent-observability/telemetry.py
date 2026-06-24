import json
import os

from config import LOG_FILE
from models import Event
from utils import timestamp


class Telemetry:

    def __init__(self, store, observer):

        self.store = store
        self.observer = observer

        os.makedirs("output", exist_ok=True)

    def emit(self, run_id, agent, event_type, message):

        event = Event(
            run_id=run_id,
            agent=agent,
            event=event_type,
            timestamp=timestamp(),
            message=message
        )

        self.store.add(event)

        self.observer.notify(event)

        with open(LOG_FILE, "a") as f:

            f.write(
                json.dumps(event.__dict__) + "\n"
            )