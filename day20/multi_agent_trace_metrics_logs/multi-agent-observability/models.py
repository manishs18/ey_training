from dataclasses import dataclass


@dataclass
class Event:
    run_id: str
    agent: str
    event: str
    timestamp: str
    message: str


@dataclass
class AgentResult:
    agent: str
    status: str
    output: str