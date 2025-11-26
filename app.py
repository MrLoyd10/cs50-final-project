import json
import sqlite3
import os
from flask import Flask, jsonify, redirect, render_template, request, flash, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from helper import isStudentExist, isUserExist, getUserById, registerUser, isUsernameExist, insertCriteria, isCriteriaSet, updateCriteria
from gradingHelper import getStudentByGrade, insertGradeToDB, createGradeDescription, getGrades, getCriteria, putGradeToDB, InitialAndTransmulatedUpdater, getFinalGrade, addDefaultGrade, updateGrade, getUpdatedInitialAndTransmulated, UpdateFinalGrade, getNaming, getTopThree


app = Flask(__name__)
app.secret_key = 'zicon'

# Define the directory where uploaded images will be stored
# This part is all for the image process
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# -----

# flask-login
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "info"
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, id, name, username, password, profile):
        self.id = id
        self.name = name
        self.username = username
        self.password = password
        self.profile = profile

@login_manager.user_loader
def load_user(user_id):
    user_info = getUserById(user_id)
    if user_info is not None:
        if user_info['profile'] is not None:
            profile_path = user_info['profile'].replace('static/', '').replace("\\", '/')
        else:
            profile_path = None
        return User(user_id, user_info['name'], user_info['username'], user_info['password'], profile_path) #add imange
    else:
        return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/")
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('userpass')

        # check if empty
        if (username == "") or (password == ""):
            flash("Please fill in all required fields.", "danger")
            return redirect("/login")
        
        user_info = isUserExist(username, password)

        if user_info is not None:
            user = User(user_info[0], user_info[1], username, user_info[3], user_info[4])
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect("/")
        else:
            flash('Invalid username or password', 'danger')
            return render_template("login.html")
    return render_template("login.html")



@app.route("/register", methods=["POST"])
def register():
    if request.method == "POST":
        name = request.form.get('name').title()
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        profile_picture = request.files['profile']
        
        # Check if its empty
        if (name == '') or (username == '') or (password == '') or (confirm_password == ''):
            flash("Please fill in all required fields.", "danger")
            return redirect("/login")
        
        if len(name) > 20:
            flash("Name should not be exceed ", "danger")
            return redirect("/login")
        
        # If the username is already exist
        if isUsernameExist(username):
            flash("Username is already exist.", "danger")
            return redirect("/login")
        
        # Validate form data (e.g., check if passwords match)
        if password != confirm_password:
            flash("Password and Confirm Password do not match. Please try again.", "warning")
            return redirect("/login")
        
        # register
        if profile_picture and allowed_file(profile_picture.filename):
            filename = secure_filename(profile_picture.filename)
            profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            profile_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        else:
            profile_path = None

        if registerUser(name, username, password, profile_path):
            flash('Registration successful. You can now log in.', 'success')
            return redirect('/login')
        else:
            flash('Registration failed. Please try again.', 'danger')
            return redirect('/login')


@app.route('/log_out')
@login_required
def log_out():
    session.clear()
    logout_user()
    return redirect('/login')




# !!! DASHBOARD PAGE
@app.route("/", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == 'POST':
        subject = request.form.get("DashSubject")
        gradelvl = request.form.get("DashGradeLvl")
        session['dashboard_subject'] = subject
        session['dashboard_gradelvl'] = gradelvl
    else:
        # using get
        subject = session.get('dashboard_subject', '')
        gradelvl = session.get('dashboard_gradelvl', '')

    user_criteria = isCriteriaSet(current_user.id)
    if user_criteria is False:
        user_criteria = (0, 0, 0, 0, 0) # id, perf, reci, seat, exam

    topThree = getTopThree(current_user.id)

    if subject and gradelvl:
        # Get all neccesary data about the student
        Perf_activities, Perf_student_grades = getGrades(gradelvl, subject, current_user.id, "Performance")
        Seat_activities, Seat_student_grades = getGrades(gradelvl, subject, current_user.id, "Seatwork")
        Reci_activities, Reci_student_grades = getGrades(gradelvl, subject, current_user.id, "Recitation")
        Exam_activities, Exam_student_grades = getGrades(gradelvl, subject, current_user.id, "Examination")

        # Get the total highest score of activities per criteria
        perfTotal = TotalScore(Perf_activities)
        seatTotal = TotalScore(Seat_activities)
        reciTotal = TotalScore(Reci_activities)
        examTotal = TotalScore(Exam_activities)
        
        # Get the criteria percentage
        CrePerf, CreSeat, CreReci, CreExam = getCriteria(current_user.id)
        
        # Put it in the database
        InsertGrade(Perf_student_grades, perfTotal, CrePerf, "performance", subject)
        InsertGrade(Seat_student_grades, seatTotal, CreSeat, "seatwork", subject)
        InsertGrade(Reci_student_grades, reciTotal, CreReci, "recitation", subject)
        InsertGrade(Exam_student_grades, examTotal, CreExam, "exam", subject)

        InitialAndTransmulatedUpdater(current_user.id)

        finalGrade = getFinalGrade(gradelvl, subject, current_user.id)

    else:
        finalGrade = []


    return render_template("dashboard.html", active="dashboard", criteria=user_criteria, topThree=topThree,
                           Dsubject=subject, Dgradelvl=gradelvl, finalGrade=finalGrade)

# !!!STUDENT MANAGER PAGE
@app.route("/student_manager")
@login_required
def student_manager():
    try:
        conn = sqlite3.connect('schoolManager.db')
        conn.row_factory = sqlite3.Row  # Set make it dictionary
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM students WHERE user_id = ? ORDER BY last_name;", (current_user.id,))
        dict_students = cursor.fetchall()
    
        conn.close()
    except Exception as e:
        flash(f"Error: {e}", "danger")
    return render_template("student_manager.html", active="student_manager", students=dict_students)

#CREATE STUDENT (STUDENT MANAGER)
@app.route("/create_student", methods=["POST"])
@login_required
def create_student():
    if request.method == 'POST':
        fname = request.form.get('fname').title()
        lname = request.form.get('lname').title()
        mname = request.form.get('mname').title()
        grade = request.form.get('grade_level')
        bday = request.form.get('b-day')
        guardian = request.form.get('parent_guardian').title()
        contact = request.form.get('contact')

        if (fname == None) or (lname == None) or (grade == None):
            flash("Please fill in all required fields.", "danger")
            return redirect("/student_manager")
        
        if isStudentExist(lname, fname, grade, current_user.id):
            flash("Student already in the class.", "danger")
            return redirect("/student_manager")
        
        last_inserted_id = None
        try:
            conn = sqlite3.connect('schoolManager.db')
            cursor = conn.cursor()

            cursor.execute("INSERT INTO students (last_name, first_name, middle_name, grade_level, birthday, guardian, contact, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (lname, fname, mname, grade, bday, guardian, contact, current_user.id))
            last_inserted_id = cursor.lastrowid

            conn.commit()
            conn.close()
            flash("Added successfully.", "success")
            
        except Exception as e:
            flash(f"Error: {e}", "danger")
        
        addDefaultGrade(last_inserted_id, grade, current_user.id)
        return redirect("/student_manager")
        



# CRITERIA SECTION
@app.route("/criteria", methods=["POST"])
@login_required
def criteria():
    if request.method == "POST":
        perf = int(request.form.get('performance'))
        reci = int(request.form.get('recitation'))
        seat = int(request.form.get('seatwork'))
        exam = int(request.form.get('examination'))
        total = perf + reci + seat + exam

        if total != 100:
            flash("The total should be 100.", "warning")
            return redirect('/')

        # If true UPDATE the criteria else INSERT
        if isCriteriaSet(current_user.id):
            updateCriteria(current_user.id, perf, reci, seat, exam)
        else:
            insertCriteria(current_user.id ,perf, reci, seat, exam)
        
        return redirect('/')
    
# !!! RECORD PAGE
@app.route("/record", methods=["POST", "GET"])
@login_required
def record():
    if request.method == 'POST':
        
        # Access the form
        criteria = request.form.get('recordCriteria')
        subject = request.form.get('recordSubject')
        gradeLvl = request.form.get('recordGradeLvl')
        title = request.form.get('recordTitle')
        highScore = request.form.get('recordHighScore')
        description_id = createGradeDescription(criteria, subject, gradeLvl, title, highScore, current_user.id)

        # Get the grade
        grades_data = json.loads(request.form.get('gradesData'))
        
        # Insert the grade into database
        for student_grade in grades_data:
            studentID = student_grade.get('studentID')
            grade = student_grade.get('grade')
            insertGradeToDB(studentID, grade, description_id)
            
        return jsonify({'message': 'Grade recorded successfully'})
    
    # Access by GET method
    else:
        return render_template("record.html", active="record")

@app.route('/search_student', methods=['POST'])
@login_required
def search_student():
    if request.method == 'POST':
        gradeLvl = request.form.get('recordGradeLvl')

        students = getStudentByGrade(gradeLvl, current_user.id)
        # Convert rows to dictionaries
        student_dicts = [dict(row) for row in students]

        return jsonify(student_dicts)

@app.route('/naming', methods=['POST'])
@login_required
def naming():
    criteria = request.form.get('criteria')
    subject = request.form.get('subject')
    gradeLevel = request.form.get('gradeLevel')
    name = getNaming(gradeLevel, subject, criteria, current_user.id)
    return str(name);


# TESTING

def TotalScore(activities):
    Total = 0
    for row in activities:
        Total += row['highest']
    return Total

def InsertGrade(student_grades, HighestTotal, CriteriaPercent, CriteriaTitle, subject):
    for data in student_grades.values():
            raw_total = sum(grade['grade'] for grade in data['grades'])
            formatted_total = round((raw_total/HighestTotal * 100) * (CriteriaPercent/100), 2)
            putGradeToDB(data['student_id'], current_user.id, CriteriaTitle, formatted_total, subject)

# !!! RESULT PAGE
@app.route("/result", methods=["POST", "GET"])
@login_required
def result():
    # !! FINISH THIS SECTION
    if request.method == 'POST':
        subject = request.form.get('resultSubject')
        gradelvl = request.form.get('resultGradeLvl')

        session['result_subject'] = subject
        session['result_gradelvl'] = gradelvl

    else:

        # This part is for GET method
        subject = session.get('result_subject', '')
        gradelvl = session.get('result_gradelvl', '')

    if subject and gradelvl:
        # Get all neccesary data about the student
        Perf_activities, Perf_student_grades = getGrades(gradelvl, subject, current_user.id, "Performance")
        Seat_activities, Seat_student_grades = getGrades(gradelvl, subject, current_user.id, "Seatwork")
        Reci_activities, Reci_student_grades = getGrades(gradelvl, subject, current_user.id, "Recitation")
        Exam_activities, Exam_student_grades = getGrades(gradelvl, subject, current_user.id, "Examination")

        # Get the total highest score of activities per criteria
        perfTotal = TotalScore(Perf_activities)
        seatTotal = TotalScore(Seat_activities)
        reciTotal = TotalScore(Reci_activities)
        examTotal = TotalScore(Exam_activities)
        
        # Get the criteria percentage
        CrePerf, CreSeat, CreReci, CreExam = getCriteria(current_user.id)

        if CrePerf == 0 and CreSeat == 0 and CreReci == 0 and CreExam == 0:
            return render_template('/result.html', active='result',
                            subject='', gradelvl='', Criteria_not_set = True,
                            Perf_activities=[], Perf_student_grades={},
                            Seat_activities=[], Seat_student_grades={},
                            Reci_activities=[], Reci_student_grades={},
                            Exam_activities=[], Exam_student_grades={},
                            finalGrade= [])
        else:
            # Put it in the database
            InsertGrade(Perf_student_grades, perfTotal, CrePerf, "performance", subject)
            InsertGrade(Seat_student_grades, seatTotal, CreSeat, "seatwork", subject)
            InsertGrade(Reci_student_grades, reciTotal, CreReci, "recitation", subject)
            InsertGrade(Exam_student_grades, examTotal, CreExam, "exam", subject)

            InitialAndTransmulatedUpdater(current_user.id)

            finalGrade = getFinalGrade(gradelvl, subject, current_user.id)

            return render_template('/result.html', active='result',
                                subject=session.get('result_subject', ''), gradelvl=session.get('result_gradelvl', ''), Criteria_not_set = False,
                                Perf_activities=Perf_activities, Perf_student_grades=Perf_student_grades,
                                Seat_activities=Seat_activities, Seat_student_grades=Seat_student_grades,
                                Reci_activities=Reci_activities, Reci_student_grades=Reci_student_grades,
                                Exam_activities=Exam_activities, Exam_student_grades=Exam_student_grades,
                                finalGrade=finalGrade)

    else:
        return render_template('/result.html', active='result',
                            subject='', gradelvl='', Criteria_not_set = False,
                            Perf_activities=[], Perf_student_grades={},
                            Seat_activities=[], Seat_student_grades={},
                            Reci_activities=[], Reci_student_grades={},
                            Exam_activities=[], Exam_student_grades={},
                            finalGrade= [])


@app.route("/update-grade", methods=["POST"])
@login_required
def update_grade():
    student_id = request.form.get('studentId')
    gradelvl = request.form.get('gradelvl')
    criteria = request.form.get('criteria')

    grade_description = request.form.get('gradeDescription')
    updated_grade = request.form.get('grade')
    subject = request.form.get('subject')

    updateResponse = updateGrade(student_id, grade_description, updated_grade)

    UpdateFinalGrade(subject, criteria, gradelvl, current_user.id, student_id)

    InitialAndTransmulatedUpdater(current_user.id)
    updatedInitialTrans = getUpdatedInitialAndTransmulated(student_id, subject, current_user.id)

    response_data = {
        'updateResponse': updateResponse,
        'updatedInitialTrans': updatedInitialTrans
    }

    return jsonify(response_data)
