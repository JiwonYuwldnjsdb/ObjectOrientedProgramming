class Student(object):
    def __init__(self, name, class_code, student_id, age):
        self.name = name
        self.class_code = class_code
        self.student_id = student_id
        self.age = age

    def get_name(self):
        return self.name

    def get_class_code(self):
        return self.class_code

    def get_student_id(self):
        return self.student_id

    def get_age(self):
        return self.age

    def get_summary(self):
        return f"name: {self.name:}\nclass code: {self.class_code}\nstudentid: {self.student_id}\nage: {self.age}"

    

student1 = Student("유지원", 2, 2208, 18)
print(student1.get_name())
print(student1.get_class_code())
print(student1.get_summary())