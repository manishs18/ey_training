class EventStore:

    def __init__(self):
        self.events = []

    def add(self, event):
        self.events.append(event)

    def get_events(self):
        return self.events

    def print_summary(self):

        print("\n========== SUMMARY ==========")

        for event in self.events:
            print(
                event.timestamp,
                event.agent,
                event.event,
                event.message
            )

        print("=============================\n")