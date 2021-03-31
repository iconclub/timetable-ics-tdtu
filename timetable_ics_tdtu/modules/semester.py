from datetime import datetime

from ics import Calendar


class Semester:
    SEMESTER_TYPE_MAP = {
        1: "HK1",
        2: "HK2",
        3: "HK Hè",
        4: "HK Dự thính 1",
        5: "HK Dự thính 2",
    }

    def __init__(self, id, type, year, start, end):
        self.id = id
        self.type = type
        self.year = year
        self.start = start
        self.end = end
        self.schedules = []

    def __str__(self):
        return "HK{type}/{year}".format(type=self.type, year=self.year)

    def __repr__(self):
        return self.__str__()

    def is_current(self):
        return self.end > datetime.now() > self.start

    def to_ics(self):
        calendar = Calendar()
        for schedule in self.schedules:
            if schedule.weeks is None:
                continue
            events = schedule.to_ics()
            for event in events:
                calendar.events.add(event)
        return calendar