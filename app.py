from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink 
from markupsafe import Markup
from sqlalchemy.exc import IntegrityError 
from wtforms.validators import ValidationError
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
class DashboardView(AdminIndexView):
    def is_visible(self):
        return False 
        
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'
        
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))
        
    @expose('/')
    def index(self):
        return redirect(url_for('users.index_view'))


class BaseAdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))
        
    def handle_view_exception(self, exc):
        if isinstance(exc, IntegrityError):
            db.session.rollback()
            flash('Error: The same class cannot be enrolled for more than once.', 'error')
            return True
        return super().handle_view_exception(exc)


# Queries for dropdown menus
def available_courses_query():
    return Course.query.outerjoin(Enrollment).group_by(Course.id).having(db.func.count(Enrollment.id) < Course.capacity)

def course_label_formatter(c):
    return f"{c.name} ({len(c.enrollments)}/{c.capacity})"

def available_students_query():
    return User.query.filter_by(role='student')


# Nested HTML Formatter
def nested_table_formatter(view, context, model, name):
    if model.role == 'student':
        if not model.enrollments:
            return Markup('<span style="color: #9ca3af; font-style: italic;">No enrollments</span>')

        html = '''
        <table style="width: 100%; min-width: 250px; border-collapse: collapse; border: 1px solid #e5e7eb; border-radius: 6px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); background: white;">
            <tr style="background-color: #f9fafb; border-bottom: 1px solid #e5e7eb;">
                <th style="padding: 6px 12px; text-align: left; font-size: 12px; color: #6b7280; font-weight: 600;">Course</th>
                <th style="padding: 6px 12px; text-align: right; font-size: 12px; color: #6b7280; font-weight: 600;">Grade</th>
            </tr>
        '''
        for e in model.enrollments:
            course_name = e.course.name if e.course else "Unknown"
            grade = f"<strong style='color: #111827;'>{e.grade}%</strong>" if e.grade is not None else '<span style="color: #9ca3af;">--</span>'
            html += f'''
            <tr style="border-bottom: 1px solid #f3f4f6;">
                <td style="padding: 6px 12px; font-size: 13px; color: #374151; font-weight: 600;">{course_name}</td>
                <td style="padding: 6px 12px; font-size: 13px; text-align: right;">{grade}</td>
            </tr>
            '''
        html += '</table>'
        return Markup(html)

    elif model.role == 'teacher':
        if not model.courses_taught:
             return Markup('<span style="color: #9ca3af; font-style: italic;">Not teaching</span>')

        html = '''
        <table style="width: 100%; min-width: 250px; border-collapse: collapse; border: 1px solid #e5e7eb; border-radius: 6px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); background: white;">
            <tr style="background-color: #f9fafb; border-bottom: 1px solid #e5e7eb;">
                <th style="padding: 6px 12px; text-align: left; font-size: 12px; color: #6b7280; font-weight: 600;">Course Taught</th>
                <th style="padding: 6px 12px; text-align: right; font-size: 12px; color: #6b7280; font-weight: 600;">Fill</th>
            </tr>
        '''
        for c in model.courses_taught:
            html += f'''
            <tr style="border-bottom: 1px solid #f3f4f6;">
                <td style="padding: 6px 12px; font-size: 13px; color: #374151; font-weight: 600;">{c.name}</td>
                <td style="padding: 6px 12px; font-size: 13px; text-align: right; color: #374151;">{len(c.enrollments)}/{c.capacity}</td>
            </tr>
            '''
        html += '</table>'
        return Markup(html)

    return Markup('<span style="color: #9ca3af;">Admin User</span>')


class UserAdminView(BaseAdminView):
    column_list = ('username', 'name', 'role', 'details') 
    column_formatters = {'details': nested_table_formatter}
    column_labels = {
        'username': 'Username',
        'name': 'Full Name',
        'role': 'Role',
        'details': 'Enrollment & Teaching Details'
    }

    inline_models = [
        (Enrollment, {
            'form_args': {
                'course': {
                    'query_factory': available_courses_query,
                    'get_label': course_label_formatter
                }
            }
        })
    ]

class CourseAdminView(BaseAdminView):
    column_list = ('name', 'teacher', 'time', 'capacity', 'roster_list')
    column_labels = {
        'name': 'Course Name',
        'teacher': 'Instructor',
        'time': 'Schedule',
        'capacity': 'Max Capacity',
        'roster_list': 'Enrolled Students'
    }

    inline_models = [
        (Enrollment, {
            'form_args': {
                'student': {
                    'query_factory': available_students_query
                }
            }
        })
    ]

# --- NEW: STUDENT ENROLLMENT DASHBOARD VIEW ---
# Instead of loading the raw Enrollment table, this loads the User table 
# but completely filters out teachers and admins!
class StudentEnrollmentView(BaseAdminView):
    
    # These two functions force this tab to ONLY show users with the 'student' role
    def get_query(self):
        return super(StudentEnrollmentView, self).get_query().filter(User.role == 'student')

    def get_count_query(self):
        return super(StudentEnrollmentView, self).get_count_query().filter(User.role == 'student')

    column_list = ('username', 'name', 'details')
    column_labels = {
        'username': 'Student ID',
        'name': 'Student Name',
        'details': 'Active Enrollments & Grades'
    }
    
    # We apply the same nested table formatter here
    column_formatters = {'details': nested_table_formatter}
    
    # We still allow you to add and edit enrollments from this view
    inline_models = [
        (Enrollment, {
            'form_args': {
                'course': {
                    'query_factory': available_courses_query,
                    'get_label': course_label_formatter
                }
            }
        })
    ]

    def on_model_change(self, form, model, is_created):
        # We ensure the 6-class limit still works here
        if is_created and model.student:
            current_count = Enrollment.query.filter_by(student_id=model.student.id).count()
            if current_count >= 6:
                raise ValidationError(f"Error: {model.student.name} is already registered for the maximum of 6 classes.")


# Register the updated views with custom tab names
admin = Admin(app, name='ACME Admin', index_view=DashboardView())
admin.add_view(UserAdminView(User, db.session, name="All Users", endpoint="users"))
admin.add_view(CourseAdminView(Course, db.session, name="Courses", endpoint="courses"))

# Notice we map our new specialized Student view to the "Enrollment" tab
admin.add_view(StudentEnrollmentView(User, db.session, name="Enrollments", endpoint="enrollments"))

admin.add_link(MenuLink(name='Sign out', category='', url='/logout'))

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
    if len(current_user.enrollments) >= 6:
        flash("You cannot register for more than 6 classes.", "error")
        return redirect(url_for('student_dashboard'))

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
    
    return redirect(url_for('teacher_dashboard', active_tab='students-enrolled', course_id=enrollment.course_id))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)