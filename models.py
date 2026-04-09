from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False) # 'student', 'teacher', or 'admin'
    name = db.Column(db.String(150))

    # This tells Flask-Admin to display the user's name instead of <User X>
    def __str__(self):
        return self.name if self.name else self.username

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, default=10)
    
    # Foreign key linking to the User table for the teacher
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    teacher = db.relationship('User', backref='courses_taught')

    # This tells Flask-Admin to display the course name instead of <Course Y>
    def __str__(self):
        return self.name

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.Integer, nullable=True)
    
    # Foreign keys
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    
    # Relationships
    student = db.relationship('User', backref='enrollments')
    course = db.relationship('Course', backref='enrollments')

    # This creates a nice readable label for the Enrollment rows
    def __str__(self):
        student_name = self.student.name if self.student else f"Student ID: {self.student_id}"
        course_name = self.course.name if self.course else f"Course ID: {self.course_id}"
        return f"{student_name} -> {course_name}"