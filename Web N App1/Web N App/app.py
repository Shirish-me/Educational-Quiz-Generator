from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt  # For password hashing

app = Flask(__name__)
app.secret_key = '5cbbba576bec58725db81d5e2d1adcf3'  # Change this to a random secret key

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')  # Update with your connection string if needed
db = client['quiz_db']
quizzes_collection = db['quizzes']
attendance_collection = db['attendance']  # Collection for attendance records
users_collection = db['users']  # Collection for user accounts

def init_db():
    """Initializes the database with default data if necessary."""
    # Check if the users collection is empty
    if users_collection.count_documents({}) == 0:
        # Add a default admin user for demonstration
        hashed_password = bcrypt.hashpw('admin'.encode('utf-8'), bcrypt.gensalt())
        users_collection.insert_one({
            'username': 'admin',
            'password': hashed_password,
            'role': 'admin'  # Admin role for the default user
        })
        print("Admin user created successfully.")
    
    # Add a dummy teacher account if it doesn't exist
    if users_collection.count_documents({'username': 'teacher1'}) == 0:
        hashed_password = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt())
        users_collection.insert_one({
            'username': 'teacher1',
            'password': hashed_password,
            'role': 'teacher'  # Role for the dummy teacher
        })
        print("Dummy teacher user created successfully.")
    
    # Add a dummy student account if it doesn't exist
    if users_collection.count_documents({'username': 'student1'}) == 0:
        hashed_password = bcrypt.hashpw('password456'.encode('utf-8'), bcrypt.gensalt())
        users_collection.insert_one({
            'username': 'student1',
            'password': hashed_password,
            'role': 'student'  # Role for the dummy student
        })
        print("Dummy student user created successfully.")

@app.route('/')
def index():
    return redirect(url_for('login'))  # Redirect to the login page

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the user exists in the database
        user = users_collection.find_one({'username': username})
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):  # Check hashed password
            session['username'] = username  # Store the username in the session
            # Redirect based on the role without explicit selection
            return redirect(url_for('student_dashboard')) if user['role'] == 'student' else redirect(url_for('teacher_dashboard'))
        
        flash('Invalid username or password', 'danger')  # Show an error message

    return render_template('login.html')  # Render the login page if GET request

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']

        # Basic validation
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'error')
            return render_template('signup.html')

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Check if username already exists
        if users_collection.find_one({'username': username}):
            flash('Username already exists. Please choose a different one.', 'error')
            return render_template('signup.html')

        # Save user information to the database
        users_collection.insert_one({
            'username': username,
            'password': hashed_password,
            'role': role
        })

        flash('Sign up successful! You can now log in.', 'success')
        return redirect(url_for('login'))  # Redirect to login page after signing up

    return render_template('signup.html')

@app.route('/teacher_dashboard')
def teacher_dashboard():
    return render_template('teacher_dashboard.html')

@app.route('/student_dashboard')  # Route for student dashboard
def student_dashboard():
    return render_template('student_dashboard.html')

@app.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    if request.method == 'POST':
        quiz_name = request.form['quiz_name']
        questions = request.form.getlist('questions[]')
        answers = request.form.getlist('answers[]')
        
        # Prepare the quiz data
        quiz_data = {
            'name': quiz_name,
            'questions': [{'question': q, 'answer': a} for q, a in zip(questions, answers)]
        }
        
        # Save the quiz data to MongoDB
        quizzes_collection.insert_one(quiz_data)
        flash('Quiz created successfully!', 'success')  # Flash message for success
        return redirect(url_for('teacher_dashboard'))  # Redirect to teacher dashboard after saving

    return render_template('create_quiz.html')

@app.route('/take_quiz', methods=['GET', 'POST'])
def take_quiz():
    if request.method == 'POST':
        quiz_id = request.form['quiz_id']
        session['quiz_id'] = quiz_id
        
        # Record attendance when quiz is taken
        attendance_collection.insert_one({
            'quiz_id': quiz_id, 
            'user_id': session.get('username', 'unknown')  # Assuming username is set in session
        })
        return redirect(url_for('quiz_questions', quiz_id=quiz_id))
    
    quizzes = quizzes_collection.find()
    return render_template('take_quiz.html', quizzes=quizzes)

@app.route('/quiz/<quiz_id>', methods=['GET', 'POST'])
def quiz_questions(quiz_id):
    quiz = quizzes_collection.find_one({'_id': ObjectId(quiz_id)})
    
    if request.method == 'POST':
        user_answers = request.form.getlist('answers[]')
        correct_answers = [q['answer'] for q in quiz['questions']]
        score = sum(1 for user_ans, correct_ans in zip(user_answers, correct_answers) if user_ans == correct_ans)
        return render_template('results.html', score=score, total=len(correct_answers))
    
    return render_template('quiz_questions.html', quiz=quiz)

@app.route('/attendance/<quiz_id>')
def attendance(quiz_id):
    attendance_records = attendance_collection.find({'quiz_id': quiz_id})
    return render_template('attendance.html', records=attendance_records)

@app.route('/generate_mcq', methods=['GET', 'POST'])
def generate_mcq_view():
    if request.method == 'POST':
        upload_option = request.form['upload_option']
        subject = request.form['subject']
        num_questions = int(request.form['num_questions'])
        score_per_question = int(request.form['score_per_question'])
        question_type = request.form['question_type']

        # Handle the uploaded file or pasted text accordingly
        if upload_option == 'pdf':
            pdf_file = request.files.get('pdf_file')
            # Process PDF file to extract questions
        elif upload_option == 'docx':
            docx_file = request.files.get('docx_file')
            # Process DOCX file to extract questions
        elif upload_option == 'text':
            input_text = request.form['input_text']
            # Process the pasted text to generate questions

        # For now, we will just display the inputs (replace with your processing logic)
        flash(f'Generated {num_questions} questions of type {question_type} for {subject}!', 'success')
        return redirect(url_for('teacher_dashboard'))  # Redirect after processing

    return render_template('generate_mcq.html')

if __name__ == '__main__':
    init_db()  # Initialize the database on startup
    app.run(debug=True)
