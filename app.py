from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import db, User, Course, Enrollment

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///university.db'

# Initialize Extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- FLASK ADMIN SETUP ---
class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

admin = Admin(app, name='ACME Admin')
admin.add_view(AdminModelView(User, db.session))
admin.add_view(AdminModelView(Course, db.session))
admin.add_view(AdminModelView(Enrollment, db.session))

# --- GENERAL ROUTES ---
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            login_user(user)
            if user.role == 'student':
                return redirect(url_for('student_dashboard'))
            elif user.role == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            elif user.role == 'admin':
                return redirect('/admin')
        else:
            flash('Invalid username or password')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- STUDENT ROUTES ---
@app.route('/student')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        return redirect(url_for('login'))
    
    all_courses = Course.query.all()
    enrolled_course_ids = [e.course_id for e in current_user.enrollments]
    
    return render_template('student.html', user=current_user, all_courses=all_courses, enrolled_course_ids=enrolled_course_ids)

@app.route('/enroll/<int:course_id>')
@login_required
def enroll_course(course_id):
    course = Course.query.get_or_404(course_id)
    if len(course.enrollments) >= course.capacity:
        flash("Class is at full capacity!")
        return redirect(url_for('student_dashboard'))
        
    existing = Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first()
    if not existing:
        new_enrollment = Enrollment(student=current_user, course=course)
        db.session.add(new_enrollment)
        db.session.commit()
    return redirect(url_for('student_dashboard'))

@app.route('/drop/<int:course_id>')
@login_required
def drop_course(course_id):
    enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first()
    if enrollment:
        db.session.delete(enrollment)
        db.session.commit()
    return redirect(url_for('student_dashboard'))

# --- TEACHER ROUTES ---
@app.route('/teacher')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        return redirect(url_for('login'))
    return render_template('teacher.html', user=current_user)

@app.route('/teacher/update_grade/<int:enrollment_id>', methods=['POST'])
@login_required
def update_grade(enrollment_id):
    if current_user.role != 'teacher':
        return redirect(url_for('login'))
        
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    if enrollment.course.teacher_id != current_user.id:
        flash("Unauthorized.")
        return redirect(url_for('teacher_dashboard'))
        
    new_grade = request.form.get('grade')
    if new_grade != "":
        enrollment.grade = int(new_grade)
    else:
        enrollment.grade = None 
        
    db.session.commit()
    flash(f"Grade updated successfully for {enrollment.student.name}!")
    
    # Updated to point back to the specific 'students-enrolled' tab
    return redirect(url_for('teacher_dashboard', active_tab='students-enrolled', course_id=enrollment.course_id))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)