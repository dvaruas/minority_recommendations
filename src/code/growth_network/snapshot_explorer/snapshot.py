class Snapshot:
    def __init__(self, event_objs=[]):
        self.events = event_objs

    def add_event(self, event_obj):
        self.events.append(event_obj)

    def add_events(self, event_obj_list=[]):
        for e in event_obj_list:
            self.add_event(event_obj=e)

    def get_events(self):
        return self.events

    def __del__(self):
        for e in self.events:
            del e

    def __str__(self):
        pass
