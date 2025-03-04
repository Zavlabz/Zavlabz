import datetime


class Homework:
    def __init__(self, text: str, days: int):
        self.text = text
        self.deadline = datetime.timedelta(days=days)
        self.created = datetime.datetime.now()

    def is_active(self) -> bool:
        return datetime.datetime.now() - self.created < self.deadline


class Student:
    def __init__(self, first_name: str, last_name: str):
        self.first_name = first_name
        self.last_name = last_name

    def do_homework(self, homework: Homework):
        if not homework.is_active():
            print("You are late")
            return None
        return homework


class Teacher:
    def __init__(self, first_name: str, last_name: str):
        self.first_name = first_name
        self.last_name = last_name

    @staticmethod #Можно использовать без использования создания класса
    def create_homework(text: str, days: int) -> Homework:
        return Homework(text, days)


if __name__ == "__main__":
    teacher = Teacher("Arina", "Strish")
    student = Student("Maxim", "Pivkin")

    print(teacher.last_name)

    expired_homework = teacher.create_homework("python classes [experiment 1]", 52)
    print(expired_homework.created)
    print(expired_homework.deadline)
    print(expired_homework.text)

    create_homework_too = teacher.create_homework
    oop_homework = create_homework_too("Create some classes about homework teacher and other goooog think", 5)
    print(oop_homework.deadline)

    student.do_homework(oop_homework)
    student.do_homework(expired_homework)
