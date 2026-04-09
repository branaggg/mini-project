from app import app
from models import db, User, Course, Enrollment

def seed_data():
    with app.app_context():
        db.drop_all()
        db.create_all()

        print("Creating users...")
        admin = User(username='admin', password='password123', role='admin', name='Admin User')
        ahepworth = User(username='ahepworth', password='password123', role='teacher', name='Ammon Hepworth')
        swalker = User(username='swalker', password='password123', role='teacher', name='Susan Walker')
        rjenkins = User(username='rjenkins', password='password123', role='teacher', name='Ralph Jenkins')
        cnorris = User(username='cnorris', password='password123', role='student', name='Chuck')
        mindy = User(username='mindy', password='password123', role='student', name='Mindy')
        aditya = User(username='aditya', password='password123', role='student', name='Aditya Ranganath')
        nancy = User(username='nancy', password='password123', role='student', name='Nancy Little')

        db.session.add_all([admin, ahepworth, swalker, rjenkins, cnorris, mindy, aditya, nancy])
        db.session.commit() 

        print("Creating courses...")
        physics121 = Course(name='Physics 121', time='TR 11:00-11:50 AM', capacity=10, teacher=swalker)
        cs106 = Course(name='CS 106', time='MWF 2:00-2:50 PM', capacity=10, teacher=ahepworth)
        math101 = Course(name='Math 101', time='MWF 10:00-10:50 AM', capacity=8, teacher=rjenkins)
        cs162 = Course(name='CS 162', time='TR 3:00-3:50 PM', capacity=4, teacher=ahepworth)

        db.session.add_all([physics121, cs106, math101, cs162])
        db.session.commit()

        print("Enrolling students...")
        db.session.add(Enrollment(student=cnorris, course=physics121))
        db.session.add(Enrollment(student=cnorris, course=cs106))
        db.session.add(Enrollment(student=mindy, course=physics121))
        db.session.add(Enrollment(student=mindy, course=cs106))
        db.session.add(Enrollment(student=mindy, course=math101))
        db.session.add(Enrollment(student=mindy, course=cs162))
        db.session.add(Enrollment(student=aditya, course=cs162, grade=92))
        db.session.add(Enrollment(student=nancy, course=cs162, grade=78))

        db.session.commit()
        print("Database seeded successfully! You can now log in.")

if __name__ == '__main__':
    seed_data()