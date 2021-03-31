import inquirer
import time
from .modules.timetable import TimeTable

def main():
    username = input("Nhập mssv: ")
    password = input("Nhập mật khẩu: ")
    start = time.time()
    timetable = TimeTable()
    timetable.set_username_password(username, password)
    semesters = timetable.get_all_semesters()
    curr_semster = [semester for semester in semesters if semester.is_current()][0]

    print("\nHọc kì hiện tại", curr_semster, "\n")
    questions = [
        inquirer.List('semester',
                      message="Chọn học kì?",
                      choices=semesters,
                      ),
    ]
    answers = inquirer.prompt(questions)

    semester = answers['semester']
    timetable.print_timetable_by_semester(semester)

    time.sleep(3)

    questions = [
        inquirer.List('export',
                      message="Xuất ra file ics?",
                      choices=["Có", "Không"]
                      ),
    ]
    answers = inquirer.prompt(questions)

    if answers['export'] == "Có":
        calendar = semester.to_ics()
        with open('tdtu.ics', 'w', encoding='utf8') as my_file:
            my_file.writelines(calendar)

    end = time.time()
    print("Thời gian thực hiện:", end - start)

if __name__ == '__main__':
    main()
