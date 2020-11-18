import json
import time
from datetime import datetime, timedelta

import arrow
import inquirer
import requests
from ics import Calendar, Event

API_URL = {
    "login": "https://stdportal.tdtu.edu.vn/taikhoan/dangnhap?ReturnUrl=http://thoikhoabieudukien.tdtu.edu.vn",
    "list_semesters": "http://thoikhoabieudukien.tdtu.edu.vn/API/XemKetQuaDangKy/LoadHocKy",
    "get_semester": "http://thoikhoabieudukien.tdtu.edu.vn/API/XemKetQuaDangKy/LoadKetQua?hocKyID={id}",
}

class Semester:
    username = ""
    password = ""

    SEMESTER_TYPE_MAP = {
        1: "HK1",
        2: "HK2",
        3: "HK Hè",
        4: "HK Dự thính 1",
        5: "HK Dự thính 2",
    }

    def __init__(self, id, type, year, start, end):
        self.type = type
        self.id = id
        self.year = year
        self.start = datetime.strptime(start, '%d/%m/%Y')
        self.end = datetime.strptime(end, '%d/%m/%Y')

    @classmethod
    def __get_session(cls):
        session = requests.Session()
        payload = "TextMSSV={username}&PassMK={password}".format(username=cls.username, password=cls.password)
        headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Referer': 'https://stdportal.tdtu.edu.vn'}
        response = session.request("POST", url=API_URL["login"], headers=headers, data=payload)
        return session

    @classmethod
    def all(cls):
        session = cls.__get_session()
        response = session.request("GET", url=API_URL["list_semesters"])
        semesters = json.loads(response.text)
        semesters = [cls(id=s['HocKyID'],
                         type=s['HocKy'],
                         year=s['NamHoc'],
                         start=s['sNgayBatDau'],
                         end=s['sNgayKetThuc']) for s in semesters if s['NamHoc'] >= 2018]
        return semesters

    @classmethod
    def from_id(cls, id):
        session = cls.__get_session()
        response = session.request("GET", url=API_URL["list_semesters"])
        semesters = json.loads(response.text)
        for s in semesters:
            if s['HocKyID'] == id and s['NamHoc']:
                return cls(id=s['HocKyID'],
                           type=s['HocKy'],
                           year=s['NamHoc'],
                           start=s['sNgayBatDau'],
                           end=s['sNgayKetThuc'])
        return None

    def __str__(self):
        return f"HK{self.type}/{self.year}"

    def __repr__(self):
        return self.__str__()

    def is_current(self):
        return self.end > datetime.now() > self.start

    def get_courses(self):
        session = self.__get_session()
        response = session.request("GET", url=API_URL["get_semester"].format(id=self.id))
        schedules = json.loads(response.text).get('list')
        schedules = [Schedule(weeks=s['CacTuanHoc'],
                              shifts=s['TietHoc'],
                              room=s['Phong'],
                              group=s['Nhom'],
                              is_practice=s['LaNhomThucHanh'],
                              course=s['TenMonHoc'],
                              date=s['Thu'],
                              semester=self) for s in schedules]
        return schedules


class Schedule:
    username = ""
    password = ""

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

    DATE_TYPE_MAP = {
        2: 0,
        3: 1,
        4: 2,
        5: 3,
        6: 4,
        7: 5,
        8: 6,
    }

    def __init__(self, weeks, shifts, room, group, is_practice, course, date, semester):
        self.semester = semester
        self.weeks = weeks.strip()
        self.shifts = shifts.strip()
        self.room = room
        self.group = group
        self.course = course
        self.date = date
        if is_practice: self.course = "Thực hành " + self.course

    @classmethod
    def __get_session(cls):
        session = requests.Session()
        payload = f"TextMSSV={username}&PassMK={password}"
        headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Referer': 'https://stdportal.tdtu.edu.vn'}
        response = session.request("POST", url=API_URL["login"], headers=headers, data=payload)
        return session

    @classmethod
    def from_id(cls, semester_id, id):
        session = cls.__get_session()
        response = session.request("GET", url=API_URL["get_semester"].format(id=semester_id))
        schedules = json.loads(response.text)['list']
        semester = Semester.from_id(semester_id)
        for s in schedules:
            if s['MonHocID'] == id:
                return cls(weeks=s['CacTuanHoc'],
                           shifts=s['TietHoc'],
                           room=s['Phong'],
                           group=s['Nhom'],
                           is_practice=s['LaNhomThucHanh'],
                           course=s['TenMonHoc'],
                           date=s['Thu'],
                           semester=Semester.from_id(semester_id))
        return None

    def __get_weeks(self):
        weeks = [pos for pos, week in enumerate(self.weeks) if week != '-']
        start = self.semester.start + timedelta(days=self.DATE_TYPE_MAP[self.date])
        return [start + timedelta(weeks=w) for w in weeks]

    def __get_shifts(self):
        shifts = [pos + 1 for pos, les in enumerate(self.shifts) if les != '-']
        return (
            self.SHIFT_START_MAP[shifts[0]],
            self.SHIFT_END_MAP[shifts[-1]],
        )

    def get_lessons(self):
        weeks = self.__get_weeks()
        shifts = self.__get_shifts()
        return [(w + shifts[0], w + shifts[1]) for w in weeks]

    def __str__(self):
        return "{course}{padding}Tuần: {weeks}\tCa: {shifts}\tThứ {date}\tPhòng: {room}".format(
            course=self.course,
            padding=" "*(50 - len(self.course)),
            weeks=self.weeks,
            shifts=self.shifts,
            date=self.date,
            room=self.room,
        )

    def __repr__(self):
        return self.__str__()

    def to_ics(self):
        lessons = self.get_lessons()
        events = []
        for lesson in lessons:
            e = Event()
            e.name = self.course
            e.location = self.room
            e.begin = arrow.get(lesson[0] - timedelta(hours=7))
            e.end = arrow.get(lesson[1] - timedelta(hours=7))
            events.append(e)
        return events


if __name__ == "__main__":
    username = input("Nhập mssv: ")
    password = input("Nhập mật khẩu: ")

    Semester.username = username
    Semester.password = password
    Schedule.username = username
    Schedule.password = password

    start = time.time()
    c = Calendar()

    semesters = Semester.all()
    curr_semster = [
        semester for semester in semesters if semester.is_current()][0]

    print("\nHọc kì hiện tại", curr_semster, "\n")

    questions = [
        inquirer.List('semester',
                      message="Chọn học kì?",
                      choices=semesters,
                      ),
    ]
    answers = inquirer.prompt(questions)

    semester = answers['semester']
    courses = semester.get_courses()
    for course in courses:
        print(course)
    print()

    time.sleep(3)

    questions = [
        inquirer.List('export',
                      message="Xuất ra file ics?",
                      choices=["Có", "Không"]
                      ),
    ]
    answers = inquirer.prompt(questions)

    if answers['export'] == "Có":
        for course in courses:
            events = course.to_ics()
            for event in events:
                c.events.add(event)
        with open('tdtu.ics', 'w') as my_file:
            my_file.writelines(c)
        print("Đã xuất ra file tdtu.ics")

    end = time.time()
    print("Thời gian thực hiện:", end - start)
