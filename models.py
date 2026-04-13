from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False) # 'student', 'teacher', or 'admin'
    name = db.Column(db.String(150))

    # NEW: Safely generates the list of classes for the Admin panel
    @property
    def class_list(self):
        if self.role == 'student':
            courses = [e.course.name for e in self.enrollments if e.course]
            return ", ".join(courses) if courses else "No classes"
        elif self.role == 'teacher':
            courses = [c.name for c in self.courses_taught]
            return ", ".join(courses) if courses else "Not teaching"
        return "N/A"

    def __str__(self):
        return self.name if self.name else self.username

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, default=10)
    
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    teacher = db.relationship('User', backref='courses_taught')

    # Prevents a teacher from being assigned to the exact same course twice
    __table_args__ = (UniqueConstraint('name', 'teacher_id', name='_teacher_course_uc'),)

    # NEW: Safely generates the roster list for the Admin panel
    @property
    def roster_list(self):
        students = [e.student.name for e in self.enrollments if e.student]
        return ", ".join(students) if students else "No students enrolled"

    def __str__(self):
        return self.name

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.Integer, nullable=True)
    
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    
    student = db.relationship('User', backref='enrollments')
    course = db.relationship('Course', backref='enrollments')

    # Prevents a student from enrolling in the exact same course twice
    __table_args__ = (UniqueConstraint('student_id', 'course_id', name='_student_course_uc'),)

    def __str__(self):
        student_name = self.student.name if self.student else f"Student ID: {self.student_id}"
        course_name = self.course.name if self.course else f"Course ID: {self.course_id}"
        return f"{student_name} -> {course_name}"