from datetime import timedelta

import arrow
from ics import Calendar, Event


class Schedule:
    DATE_TYPE_MAP = {
        2: 0,
        3: 1,
        4: 2,
        5: 3,
        6: 4,
        7: 5,
        8: 6,
    }

    SHIFT_START_MAP = {
        1: timedelta(hours=6, minutes=50),
        2: timedelta(hours=7, minutes=35),
        3: timedelta(hours=8, minutes=20),

        4: timedelta(hours=9, minutes=25),
        5: timedelta(hours=10, minutes=10),
        6: timedelta(hours=10, minutes=55),

        7: timedelta(hours=12, minutes=30),
        8: timedelta(hours=13, minutes=15),
        9: timedelta(hours=14, minutes=0),

        10: timedelta(hours=15, minutes=5),
        11: timedelta(hours=15, minutes=50),
        12: timedelta(hours=16, minutes=35),

        13: timedelta(hours=17, minutes=45),
        14: timedelta(hours=18, minutes=30),
        15: timedelta(hours=19, minutes=15),
        16: timedelta(hours=20, minutes=00),
    }

    SHIFT_END_MAP = {
        1: SHIFT_START_MAP[2],
        2: SHIFT_START_MAP[3],
        3: timedelta(hours=9, minutes=15),

        4: SHIFT_START_MAP[5],
        5: SHIFT_START_MAP[6],
        6: timedelta(hours=11, minutes=50),

        7: SHIFT_START_MAP[7],
        8: SHIFT_START_MAP[8],
        9: timedelta(hours=14, minutes=55),

        10: SHIFT_START_MAP[11],
        11: SHIFT_START_MAP[12],
        12: timedelta(hours=17, minutes=30),

        13: SHIFT_START_MAP[14],
        14: SHIFT_START_MAP[15],
        15: SHIFT_START_MAP[16],
        16: timedelta(hours=21, minutes=00),
    }

    def __init__(
        self,
        course_id,
        course_name,
        group,
        subgroup,
        room,
        date_of_week,
        num_times,
        begin_time,
        weeks,
        semester,
    ):
        self.course_id    = course_id    # MaMH
        self.course_name  = course_name  # TenMonHoc
        self.group        = group        # Nhom
        self.subgroup     = subgroup     # ToTH
        self.room         = room         # Phong
        self.date_of_week = date_of_week # Thu
        self.begin_time   = begin_time   # TietBatDau
        self.num_times    = num_times    # SoTiet
        self.weeks        = weeks        # Tuan
        self.semester     = semester
        semester.schedules.append(self)

        """Example API
        {
            "MaMH": "301003",
            "Nhom": "112",
            "Phong": "HOCTRUCTUY",
            "SoTiet": 3,
            "TenMonHoc": "Đường lối cách mạng của Đảng Cộng sản Việt Nam",
            "Thu": 2,
            "TietBatDau": 10,
            "ToTH": "  ",
            "Tuan": "-----6---------------------------------------------"
        }
        """

    def __str__(self):
        return "{course_id}-{course_name}".format(
            course_id=self.course_id,
            course_name=self.course_name,
        )

    def __repr__(self):
        return self.__str__()

    def __get_weeks(self):
        weeks = [pos for pos, week in enumerate(self.weeks) if week != '-']
        start = self.semester.start + \
            timedelta(days=self.DATE_TYPE_MAP[self.date_of_week])
        return [start + timedelta(weeks=w) for w in weeks]

    def __get_shifts(self):
        return (
            self.SHIFT_START_MAP[self.begin_time],
            self.SHIFT_END_MAP[self.begin_time + self.num_times - 1],
        )

    def get_lessons(self):
        weeks = self.__get_weeks()
        shifts = self.__get_shifts()
        return [(w + shifts[0], w + shifts[1]) for w in weeks]

    def to_ics(self):
        lessons = self.get_lessons()
        return list(map(lambda lesson: Event(
            name=self.course_name,
            location=self.room,
            begin=arrow.get(lesson[0] - timedelta(hours=7)),
            end=arrow.get(lesson[1] - timedelta(hours=7))
        ), lessons))