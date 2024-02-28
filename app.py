import os
import joblib
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'hamza'

with open('DecisionTreeClassifier.pkl', 'rb') as file:
    model = joblib.load(file)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


if not os.path.exists('users.db'):
    with app.app_context():

        db.create_all()

# Registration route
@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']


        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error_message = 'Username already exists. Please choose a different username.'
            return render_template('register.html', error_message=error_message)


        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()


        return redirect(url_for('login'))


    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']


        user = User.query.filter_by(username=username).first()
        if user and user.password == password:

            session['logged_in'] = True
            session['username'] = username


            return redirect(url_for('dashboard'))
        else:

            error_message = 'Invalid username or password. Please try again.'
            return render_template('login.html', error_message=error_message)


    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():

    if not session.get('logged_in'):

        return redirect(url_for('login'))

    if request.method == 'POST':

        gender = request.form['gender']
        age = int(request.form['age'])
        hypertension = int(request.form['hypertension'])
        heart_disease = int(request.form['heart_disease'])
        smoking_history = request.form['smoking_history']
        bmi = float(request.form['bmi'])
        HbA1c_level = float(request.form['HbA1c_level'])
        blood_glucose_level = float(request.form['blood_glucose_level'])


        input_data = [[gender, age, hypertension, heart_disease, smoking_history, bmi, HbA1c_level, blood_glucose_level]]
        diabetes_type = model.predict(input_data)[0]


        diabetes_labels = {
            0: 'Type 1 Diabetes',
            1: 'Type 2 Diabetes',
            2: 'Gestational Diabetes',
            3: 'Prediabetes',
            4: 'No Diabetes'
        }
        diabetes_type_label = diabetes_labels.get(diabetes_type, 'Unknown')


        return render_template('dashboard.html', prediction=diabetes_type_label)

    return render_template('dashboard.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 8080)
