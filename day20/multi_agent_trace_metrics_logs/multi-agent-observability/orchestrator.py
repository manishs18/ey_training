from agents.planner import Planner
from agents.researcher import Researcher
from agents.writer import Writer
from agents.reviewer import Reviewer

from event_store import EventStore
from observer import ProgressObserver
from telemetry import Telemetry

from utils import generate_run_id


class Orchestrator:

    def __init__(self):

        self.store = EventStore()
        self.observer = ProgressObserver()
        self.telemetry = Telemetry(
            self.store,
            self.observer
        )

    def execute(self, task):

        run_id = generate_run_id()

        planner = Planner()
        researcher = Researcher()
        writer = Writer()
        reviewer = Reviewer()

        self.telemetry.emit(
            run_id,
            "Planner",
            "START",
            "Planning started"
        )

        plan = planner.run(task)

        self.telemetry.emit(
            run_id,
            "Planner",
            "SUCCESS",
            "Planning completed"
        )

        self.telemetry.emit(
            run_id,
            "Researcher",
            "START",
            "Research started"
        )

        research = researcher.run(plan)

        self.telemetry.emit(
            run_id,
            "Researcher",
            "SUCCESS",
            "Research completed"
        )

        self.telemetry.emit(
            run_id,
            "Writer",
            "START",
            "Writing started"
        )

        article = writer.run(research)

        self.telemetry.emit(
            run_id,
            "Writer",
            "SUCCESS",
            "Writing completed"
        )

        self.telemetry.emit(
            run_id,
            "Reviewer",
            "START",
            "Review started"
        )

        result = reviewer.run(article)

        self.telemetry.emit(
            run_id,
            "Reviewer",
            "SUCCESS",
            "Review completed"
        )

        self.store.print_summary()

        print(result)