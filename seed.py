import random
from app import app
from models import db, User, Course, Enrollment

def seed_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        print("Creating Admin and Teachers...")
        
        # Admin
        admin = User(username='admin', password='password123', role='admin', name='System Admin')
        
        # Teachers
        tmath = User(username='tmath', password='password123', role='teacher', name='Dr. Alan Turing')
        tphys = User(username='tphys', password='password123', role='teacher', name='Dr. Marie Curie')
        tcse = User(username='tcse', password='password123', role='teacher', name='Dr. Ada Lovelace')
        teng = User(username='teng', password='password123', role='teacher', name='Dr. Mary Shelley')
        this = User(username='this', password='password123', role='teacher', name='Dr. Herodotus')
        
        db.session.add_all([admin, tmath, tphys, tcse, teng, this])
        db.session.commit()

        print("Creating 10 courses...")
        
        # Courses
        math131 = Course(name='MATH 131', time='MWF 8:00-8:50 AM', capacity=30, teacher=tmath)
        math250 = Course(name='MATH 250', time='TR 9:30-10:45 AM', capacity=30, teacher=tmath)
        phys102 = Course(name='PHYS 102', time='MWF 10:00-10:50 AM', capacity=30, teacher=tphys)
        phys220 = Course(name='PHYS 220', time='TR 11:00-12:15 PM', capacity=30, teacher=tphys)
        cse234 = Course(name='CSE 234', time='MWF 1:00-1:50 PM', capacity=30, teacher=tcse)
        cse350 = Course(name='CSE 350', time='TR 2:00-3:15 PM', capacity=30, teacher=tcse)
        eng101 = Course(name='ENG 101', time='MWF 11:00-11:50 AM', capacity=30, teacher=teng)
        eng205 = Course(name='ENG 205', time='TR 1:00-2:15 PM', capacity=30, teacher=teng)
        his110 = Course(name='HIS 110', time='MWF 3:00-3:50 PM', capacity=30, teacher=this)
        his300 = Course(name='HIS 300', time='TR 3:30-4:45 PM', capacity=30, teacher=this)

        # Store courses in a list so we can randomly pick from them later
        created_courses = [math131, math250, phys102, phys220, cse234, cse350, eng101, eng205, his110, his300]
        
        db.session.add_all(created_courses)
        db.session.commit()

        print("Creating 50 explicit students with ultra-short usernames...")
        
        # 50 Explicit Students (a-z, then 1-24)
        students = [
            User(username='a', password='password123', role='student', name='James Smith'),
            User(username='b', password='password123', role='student', name='Mary Johnson'),
            User(username='c', password='password123', role='student', name='John Williams'),
            User(username='d', password='password123', role='student', name='Patricia Brown'),
            User(username='e', password='password123', role='student', name='Robert Jones'),
            User(username='f', password='password123', role='student', name='Jennifer Garcia'),
            User(username='g', password='password123', role='student', name='Michael Miller'),
            User(username='h', password='password123', role='student', name='Linda Davis'),
            User(username='i', password='password123', role='student', name='William Rodriguez'),
            User(username='j', password='password123', role='student', name='Elizabeth Martinez'),
            
            User(username='k', password='password123', role='student', name='David Hernandez'),
            User(username='l', password='password123', role='student', name='Barbara Lopez'),
            User(username='m', password='password123', role='student', name='Richard Gonzalez'),
            User(username='n', password='password123', role='student', name='Susan Wilson'),
            User(username='o', password='password123', role='student', name='Joseph Anderson'),
            User(username='p', password='password123', role='student', name='Jessica Thomas'),
            User(username='q', password='password123', role='student', name='Thomas Taylor'),
            User(username='r', password='password123', role='student', name='Sarah Moore'),
            User(username='s', password='password123', role='student', name='Charles Jackson'),
            User(username='t', password='password123', role='student', name='Karen Martin'),
            
            User(username='u', password='password123', role='student', name='Christopher Lee'),
            User(username='v', password='password123', role='student', name='Lisa Perez'),
            User(username='w', password='password123', role='student', name='Daniel Thompson'),
            User(username='x', password='password123', role='student', name='Nancy White'),
            User(username='y', password='password123', role='student', name='Matthew Harris'),
            User(username='z', password='password123', role='student', name='Betty Sanchez'),
            
            User(username='1', password='password123', role='student', name='Anthony Clark'),
            User(username='2', password='password123', role='student', name='Margaret Ramirez'),
            User(username='3', password='password123', role='student', name='Mark Lewis'),
            User(username='4', password='password123', role='student', name='Sandra Robinson'),
            User(username='5', password='password123', role='student', name='Donald Walker'),
            User(username='6', password='password123', role='student', name='Ashley Young'),
            User(username='7', password='password123', role='student', name='Steven Allen'),
            User(username='8', password='password123', role='student', name='Kimberly King'),
            User(username='9', password='password123', role='student', name='Paul Wright'),
            User(username='10', password='password123', role='student', name='Emily Scott'),
            
            User(username='11', password='password123', role='student', name='Andrew Torres'),
            User(username='12', password='password123', role='student', name='Donna Nguyen'),
            User(username='13', password='password123', role='student', name='Joshua Hill'),
            User(username='14', password='password123', role='student', name='Michelle Flores'),
            User(username='15', password='password123', role='student', name='Kenneth Green'),
            User(username='16', password='password123', role='student', name='Carol Adams'),
            User(username='17', password='password123', role='student', name='Kevin Nelson'),
            User(username='18', password='password123', role='student', name='Amanda Baker'),
            User(username='19', password='password123', role='student', name='Brian Hall'),
            User(username='20', password='password123', role='student', name='Melissa Rivera'),
            
            User(username='21', password='password123', role='student', name='George Campbell'),
            User(username='22', password='password123', role='student', name='Deborah Mitchell'),
            User(username='23', password='password123', role='student', name='Edward Carter'),
            User(username='24', password='password123', role='student', name='Stephanie Roberts')
        ]

        db.session.add_all(students)
        db.session.commit()

        print("Randomly enrolling students into courses...")
        
        # Loop through every student and randomly assign them to classes
        for student in students:
            # Randomly decide if they are taking 2, 3, or 4 classes
            num_classes = random.randint(2, 4)
            
            # Select unique courses from the list so they don't enroll in the same class twice
            selected_courses = random.sample(created_courses, num_classes)
            
            for course in selected_courses:
                # 70% chance they have a grade between 60 and 100, 30% chance it is empty
                if random.random() > 0.3:
                    grade = random.randint(60, 100)
                else:
                    grade = None
                    
                enrollment = Enrollment(student=student, course=course, grade=grade)
                db.session.add(enrollment)

        db.session.commit()

        print("Database seeded successfully with explicit data and random enrollments! You can now log in.")

if __name__ == '__main__':
    seed_data()