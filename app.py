from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify, send_from_directory
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
import io
import base64
import os
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Secret key for session management

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine('sqlite:///users.db')
Session = sessionmaker(bind=engine)
db_session = Session()

# Define User model
class User(Base):
    __tablename__ = 'users'
    username = Column(String, primary_key=True)
    password = Column(String)

# Create the users table if it doesn't exist
Base.metadata.create_all(engine)

# Load and preprocess the dataset
data = pd.read_csv("kidney_disease.csv", encoding='latin1')

# Data Cleaning and Preprocessing
data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)
categorical_columns = ['rbc', 'pc', 'pcc', 'ba', 'htn', 'dm', 'cad', 'appet', 'pe', 'ane', 'type_of_kidney_disease']
le = LabelEncoder()
for column in categorical_columns:
    data[column] = le.fit_transform(data[column].astype(str))
data.replace('?', np.nan, inplace=True)
data = data.apply(pd.to_numeric, errors='coerce')
data = data.fillna(data.median())

# Define features and target
X = data[['pcv', 'sc', 'hemo', 'sg', 'rc']]
y = data['type_of_kidney_disease']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Logistic Regression Model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check the credentials from the database
        user = db_session.query(User).filter_by(username=username).first()
        if user and user.password == password:
            session['logged_in'] = True
            return redirect(url_for('predict_page'))
        error = 'Invalid Credentials. Please try again.'
        return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists
        if db_session.query(User).filter_by(username=username).first():
            error = 'Username already exists. Please choose a different username.'
            return render_template('register.html', error=error)

        # Add the new user to the database
        new_user = User(username=username, password=password)
        db_session.add(new_user)
        db_session.commit()

        # Export the updated user list to Excel
        export_users_to_excel()

        flash("Registration successful. Please log in.")
        return redirect(url_for('login'))
    return render_template('register.html')

def export_users_to_excel():
    users = db_session.query(User).all()
    df = pd.DataFrame([(user.username, user.password) for user in users], columns=['username', 'password'])
    df.to_excel('users_backup.xlsx', index=False)  # Changed file name

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']

        # Retrieve the password from the database based on the username
        user = db_session.query(User).filter_by(username=username).first()
        if user:
            flash(f"Your password is: {user.password}", 'success')
        else:
            flash("Username not found. Please try again.", 'error')
        return redirect(url_for('login'))
    return render_template('forgot_password.html')

@app.route('/predict_page')
def predict_page():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    try:
        # Ensure all input fields are provided and can be converted to float
        pcv = request.form.get('pcv', '').strip()
        sc = request.form.get('sc', '').strip()
        hemo = request.form.get('hemo', '').strip()
        sg = request.form.get('sg', '').strip()
        rc = request.form.get('rc', '').strip()

        if not (pcv and sc and hemo and sg and rc):
            flash("All input fields are required. Please provide valid numbers.")
            return redirect(url_for('predict_page'))
        
        # Convert inputs to float
        pcv = float(pcv)
        sc = float(sc)
        hemo = float(hemo)
        sg = float(sg)
        rc = float(rc)

        # Create input array for prediction
        input_data = np.array([[pcv, sc, hemo, sg, rc]])
        prediction = model.predict(input_data)
        kidney_disease_type_encoded = prediction[0]
        kidney_disease_type = le.inverse_transform([kidney_disease_type_encoded])[0]
        result = f"Type of Kidney Disease: {kidney_disease_type}"
        treatment = "Please consult a healthcare professional for further diagnosis and treatment."
    except ValueError:
        flash("Invalid input. Please enter valid numbers.")
        return redirect(url_for('predict_page'))
    return render_template('result.html', result=result, treatment=treatment)

@app.route('/dataset')
def dataset():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    dataset_sample = data.head()
    return render_template('dataset.html', data=dataset_sample.to_html())

@app.route('/confusion_matrix')
def confusion_matrix():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    from sklearn.metrics import confusion_matrix
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    return render_template('confusion_matrix.html', cm=cm)

@app.route('/random_graph')
def random_graph():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    ax.plot(x, y)
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)
    return render_template('random_graph.html', plot_url=plot_url)

@app.route('/doctors')
def doctors():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    doctors_info = [
        {"name": "Dr. Smith", "contact": "1234567890", "location": "New York"},
        {"name": "Dr. Johnson", "contact": "0987654321", "location": "Los Angeles"},
        {"name": "Dr. Brown", "contact": "1122334455", "location": "Chicago"},
        {"name": "Dr. Williams", "contact": "5566778899", "location": "Houston"},
    ]
    random.shuffle(doctors_info)
    return render_template('doctors.html', doctors=doctors_info)

@app.route('/solutions')
def solutions():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    solution_text = "AI Generated Solutions and Treatments: Regular exercise, balanced diet, and proper hydration are recommended."
    return render_template('solutions.html', solution=solution_text)

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))

@app.route('/analyze')
def analyze():
    if not session.get('logged_in'):  # Corrected this line
        return redirect(url_for('login'))
    return render_template('analyze.html')

@app.route('/chatbot', methods=['POST'])
def chatbot():
    questions = [
        "Do you experience any swelling in your ankles or feet?",
        "Have you noticed any changes in urination frequency?",
        "Do you have a history of high blood pressure?",
        "Do you experience any pain or discomfort in your lower back?",
        "Have you noticed any blood in your urine?",
        "Do you have a family history of kidney disease?",
        "Have you experienced any nausea or vomiting recently?",
        "Do you have a history of diabetes?",
        "Have you experienced any shortness of breath?",
        "Do you feel tired or fatigued frequently?"
    ]
    answers = request.json.get('answers')
    if len(answers) < 10:
        question = questions[len(answers)]
        return jsonify({"question": question, "end": False})
    else:
        risk = sum(1 for answer in answers if answer.lower() == 'yes')
        if risk >= 5:
            prescription = "You might be at risk of kidney disease. Please consult a healthcare professional."
        else:
            prescription = "Your responses indicate a lower risk, but consider regular check-ups."
        return jsonify({"prescription": prescription, "end": True})

if __name__ == '__main__':
    app.run(debug=True)
