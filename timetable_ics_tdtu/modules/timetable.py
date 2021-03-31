import json
import requests
from datetime import datetime
from prettytable import PrettyTable

from .semester import Semester
from .schedule import Schedule

KEY = "b0137f5d2a04529b8f5274bbdbaa194e"[::-1]
URL_API = {
    "list_semester": "http://thoikhoabieudukien.tdtu.edu.vn/API/XemKetQuaDangKy/LoadHocKy",
    "list_schedule": "http://mobiservice.tdt.edu.vn/Service1.svc/LayTKBTHeoHocKyService"
}

class TimeTable:

    def __init__(self):
        self.username = ""
        self.username = ""

    def set_username_password(self, username, password):
        self.username = username
        self.password = password

    def get_all_semesters(self):
        response = requests.get(url=URL_API["list_semester"])
        semesters = json.loads(response.text)
        semesters = [Semester(id=s['HocKyID'],
                              type=s['HocKy'],
                              year=s['NamHoc'],
                              start=datetime.strptime(s['sNgayBatDau'], '%d/%m/%Y'),
                              end=datetime.strptime(s['sNgayKetThuc'], '%d/%m/%Y')) for s in semesters if s['NamHoc'] >= 2018]
        return semesters

    def get_semester(self, semester_id):
        semesters = self.get_all_semesters()
        _semester = list(filter(lambda x: x.id == semester_id, semesters))
        return _semester[0] if len(_semester) else None

    def __prepare_payload(self, semester, year):
        username = self.username
        password = self.password
        payload = {
            "Key": KEY,
            "MSSV": username,
            "MatKhau": password,
            "NamHoc": year,
            "HocKy": semester
        }
        return json.dumps(payload)

    def get_all_schedules(self, semester):
        headers = {'Content-Type': 'application/json'}
        payload = self.__prepare_payload(semester.type, semester.year)
        response = requests.post(url = URL_API["list_schedule"], data = payload, headers = headers)
        schedules = json.loads(response.text)
        return list(map(lambda schedule: Schedule(
                course_id = schedule['MaMH'],
                course_name = schedule['TenMonHoc'],
                group = schedule['Nhom'],
                subgroup = schedule['ToTH'],
                room = schedule['Phong'],
                date_of_week = schedule['Thu'],
                num_times = schedule['SoTiet'],
                begin_time = schedule['TietBatDau'],
                weeks = schedule['Tuan'],
                semester = semester
            ), schedules))

    def print_timetable_by_semester(self, semester):
        schedules = self.get_all_schedules(semester)
        table = PrettyTable()
        table.field_names = ['MaMH', 'TenMonHoc', 'Nhom', 'ToTH', 'Phong', 'Tuan']
        for schedule in schedules:
            table.add_row([schedule.course_id, schedule.course_name, schedule.group, schedule.subgroup, schedule.room, schedule.weeks])
        print(table)