from orchestrator import Orchestrator


def main():
    task = "Write a blog about Multi-Agent Observability"

    orchestrator = Orchestrator()
    orchestrator.execute(task)


if __name__ == "__main__":
    main()