import datetime
from collections import defaultdict


class DeadlineError(Exception):
    pass


class Person:
    def __init__(self, first_name: str, last_name: str):
        self.first_name = first_name
        self.last_name = last_name


class Homework:
    def __init__(self, text: str, days: int):
        self.text = text
        self.deadline = datetime.timedelta(days=days)
        self.created = datetime.datetime.now()

    def is_active(self) -> bool:
        return datetime.datetime.now() - self.created < self.deadline


class HomeworkResult:
    def __init__(self, author: 'Student', homework: Homework, solution: str):
        if not isinstance(homework, Homework):
            raise TypeError("You gave a not Homework object")

        self.homework = homework
        self.solution = solution
        self.author = author
        self.created = datetime.datetime.now()


class Student(Person):
    def do_homework(self, homework: Homework, solution: str) -> HomeworkResult:
        if not homework.is_active():
            raise DeadlineError("You are late")
        return HomeworkResult(self, homework, solution)


class Teacher(Person):
    homework_done = defaultdict(set)

    @staticmethod
    def create_homework(text: str, days: int) -> Homework:
        return Homework(text, days)

    def check_homework(self, result: HomeworkResult) -> bool:
        if len(result.solution) > 5:
            self.homework_done[result.homework].add(result)
            return True
        return False

    @classmethod
    def reset_results(cls, homework: Homework = None):
        if homework:
            cls.homework_done.pop(homework, None)
        else:
            cls.homework_done.clear()


if __name__ == '__main__':
    opp_teacher = Teacher('Arina', 'Strizh')
    advanced_python_teacher = Teacher('Aleksandr', 'Smetanin')

    lazy_student = Student('Misha', 'Elsufiev')
    good_student = Student('Pivkin', 'Maxim')

    oop_hw = opp_teacher.create_homework('Learn OOP', 1)
    docs_hw = opp_teacher.create_homework('Read docs', 5)

    result_1 = good_student.do_homework(oop_hw, 'I have done this hw')
    result_2 = good_student.do_homework(docs_hw, 'I have done this hw too')
    result_3 = lazy_student.do_homework(docs_hw, 'done')
    try:
        result_4 = HomeworkResult(good_student, "fff", "Solution")
    except Exception:
        print('There was an exception here')
    opp_teacher.check_homework(result_1)
    temp_1 = opp_teacher.homework_done

    advanced_python_teacher.check_homework(result_1)
    temp_2 = Teacher.homework_done
    assert temp_1 == temp_2

    opp_teacher.check_homework(result_2)
    opp_teacher.check_homework(result_3)

    print(Teacher.homework_done[oop_hw])
    Teacher.reset_results()
