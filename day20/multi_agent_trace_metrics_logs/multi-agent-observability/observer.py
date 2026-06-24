class ProgressObserver:

    def notify(self, event):

        print(
            f"[{event.timestamp}] "
            f"{event.agent} -> "
            f"{event.event} : "
            f"{event.message}"
        )