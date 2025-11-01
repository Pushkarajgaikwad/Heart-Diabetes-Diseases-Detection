from flask import Flask, request, url_for, redirect, render_template, session, flash
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
import re
from flask_mail import Mail, Message

import pickle
import numpy as np



model = pickle.load(open('models/framingham.pickle', 'rb'))
model1 = pickle.load(open('models/combine_heart.pickle', 'rb'))
model2 = pickle.load(open('models/diabetes_prediction_rf.pickle', 'rb'))
app = Flask(__name__, template_folder='templates')
bcrypt = Bcrypt(app)
users = []  # Initialize the users list for temporary storage
app.secret_key = 'ThisIsMySicretKey'  # Set a secret key for the app

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Aditya@2011'
app.config['MYSQL_DB'] = 'myflaskapp'  # Name of your MySQL database
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # Return rows as dictionaries
app.config['TESTING']=True

mysql = MySQL(app)


@app.route('/index')
def index():
    return render_template('index.html')


@app.route("/heart")
def heart():
    return render_template('heart.html')

@app.route("/heartframg", methods=['GET'])
def heartf():
    return render_template("heartfram.html")

@app.route("/heartcombine", methods=['GET'])
def heartc():
    return render_template("heartcombined.html")

@app.route('/diabetes')
def diabetes():
    return render_template('diabetes.html')

@app.route('/healthtips')
def healthtips():
    return render_template('healthtips.html')

@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email_or_phone = request.form['email_or_phone']
        password = request.form['password']

        # Check if email or phone number already exists
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email_or_phone = %s", (email_or_phone,))
        existing_user = cur.fetchone()

        if existing_user:
            cur.close()
            flash('This email or phone number is already in use. Please use a different one.', 'error')
            return redirect(url_for('register'))

        # Server-side validation for email or phone number format
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.[\w\.-]+$', email_or_phone) and not re.match(r'^\d{10}$', email_or_phone):
            flash('Please enter a valid email or a 10-digit phone number.', 'error')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # If email or phone number is unique and format is correct, proceed with registration
        cur.execute("INSERT INTO users (name, email_or_phone, password) VALUES (%s, %s, %s)",
                    (name, email_or_phone, hashed_password))
        mysql.connection.commit()
        cur.close()

        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/send_email', methods=['POST'])
def send_email():
    if request.method == 'POST':
        full_name = request.form['full_name']
        phone_number = request.form['phone_number']
        email = request.form['email']
        address = request.form['address']
        message = request.form['message']

        msg = Message('New Contact Request', recipients=['adityapawar3602@gmail.com'])  # Change this to your recipient email address
        msg.body = f"Full Name: {full_name}\nPhone Number: {phone_number}\nEmail: {email}\nAddress: {address}\nMessage: {message}"

        try:
            mail.send(msg)
            flash('Your message has been sent successfully!', 'success')
        except Exception as e:
            flash('An error occurred while sending your message. Please try again later.', 'error')
            app.logger.error(f"Error sending email: {str(e)}")

        return redirect(url_for('index'))  # Redirect the user back to the index page after sending the email

    return redirect(url_for('register'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_phone = request.form['email_or_phone']
        password = request.form['password']

        # MySQL Database Interaction
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email_or_phone = %s", (email_or_phone,))
        user = cur.fetchone()
        cur.close()

        if user:
            if bcrypt.check_password_hash(user['password'], password):
                # Set user information in the session
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                flash('Login successful. Welcome back!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid email/phone or password. Please try again.', 'error')
        else:
            flash('You are not registered. Please register.', 'error')
            return redirect(url_for('register'))  # Redirect to registration page

    return render_template('login.html')


@app.route('/profile')
def profile():
    user_name = session.get('user_name')
    user_id = session.get('user_id')

    if not user_name or not user_id:
        flash('Please log in to access your profile.', 'error')
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    # Fetch heart framingham results
    cur.execute("SELECT * FROM heart_fram_results WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    heart_fram_results = cur.fetchall()

    # Fetch heart combined results
    cur.execute("SELECT * FROM heart_combined_results WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    heart_combined_results = cur.fetchall()

    # Fetch diabetes results
    cur.execute("SELECT * FROM diabetes_results WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    diabetes_results = cur.fetchall()

    cur.close()

    return render_template('profile.html', user_name=user_name, heart_fram_results=heart_fram_results, heart_combined_results=heart_combined_results, diabetes_results=diabetes_results)


@app.route("/heartfram", methods=['GET', 'POST'])
def heartfram():
    if request.method == 'POST':
        gender = request.form['gender']
        gender = 1 if gender == 'Male' else 0

        age = int(request.form['age'])
        smoker = request.form['smoker']
        smoker = 1 if smoker == 'Yes' else 0

        cigs = int(request.form['cigs'])
        bp_meds = request.form['bp_meds']
        bp_meds = 1 if bp_meds == 'Yes' else 0
        stroke = request.form['stroke']
        stroke = 1 if stroke == 'Yes' else 0
        hyp = request.form['hyp']
        hyp = 1 if hyp == 'Yes' else 0
        dia = 1  # Assuming diabetes is always yes
        chol = int(request.form['chol'])
        sysBp = int(request.form['sysBp'])
        diaBp = int(request.form['diaBp'])
        height = float(request.form['height'])
        weight = int(request.form['weight'])
        bmi = weight / (height * height)
        rate = int(request.form['rate'])
        glu = float(request.form['glu'])

        prediction = model.predict(np.array([gender, age, smoker, cigs, bp_meds, stroke, hyp, dia, chol, sysBp, diaBp, bmi, rate, glu]).reshape((1, -1)))
        output = round(prediction[0])

        user_id = session.get('user_id')
        if user_id:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO heart_fram_results (user_id, gender, age, smoker, cigs, bp_meds, stroke, hyp, dia, chol, sysBp, diaBp, bmi, rate, glu, prediction)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, gender, age, smoker, cigs, bp_meds, stroke, hyp, dia, chol, sysBp, diaBp, bmi, rate, glu, output))
            mysql.connection.commit()
            cur.close()

        prediction_message = "No significant risk detected. Maintain your healthy lifestyle." if output == 0 else "Your data indicates a high risk of heart failure. Seek medical attention promptly."

        parameters = {
            'Gender': (gender, (0, 1)),
            'Age': (age, (0, 100)),
            'Smoker': (smoker, (0, 1)),
            'Cigs per Day': (cigs, (0, 30)),
            'BP Medication': (bp_meds, (0, 1)),
            'Stroke': (stroke, (0, 1)),
            'Hypertension': (hyp, (0, 1)),
            'Diabetes': (dia, (0, 1)),
            'Cholesterol': (chol, (125, 200)),
            'Systolic BP': (sysBp, (90, 120)),
            'Diastolic BP': (diaBp, (60, 80)),
            'BMI': (bmi, (18.5, 24.9)),
            'Heart Rate': (rate, (60, 100)),
            'Glucose': (glu, (70, 140))
        }

        exceeded_parameters = {key: value for key, value in parameters.items() if value[0] < value[1][0] or value[0] > value[1][1]}

        return render_template('result.html', prediction=prediction_message, exceeded_parameters=exceeded_parameters)
    else:
        return render_template('heartfram.html')



@app.route('/heartcombined', methods=['GET', 'POST'])
def heartcombined():
    if request.method == 'POST':
        age = int(request.form['age'])
        sex = request.form['sex']
        sex = 1 if sex == 'Male' else 0
        cpt = request.form['cpt']
        cpt = {'Typical Angina': 0, 'Atypical Angina': 1, 'Non-Anginal Pain': 2, 'Asymptomatic': 3}.get(cpt, 3)
        bp = int(request.form['bp'])
        chol = int(request.form['chol'])
        fbp = request.form['fbp']
        fbp = 0 if fbp == 'Fasting Blood Sugar < 120 mg/dl' else 1
        ecg = request.form['ecg']
        ecg = {'Resting ECG': 0, 'ST-T wave abnormality': 1, 'Left ventricular hypertrophy': 2}.get(ecg, 0)
        mhr = int(request.form['mhr'])
        exe_angina = request.form['exe_angina']
        exe_angina = 1 if exe_angina == 'Yes' else 0
        oldpeak = float(request.form['oldpeak'])
        slope = request.form['slope']
        slope = {'Upsloping': 1, 'Flat': 2, 'Downsloping': 3}.get(slope, 1)

        prediction1 = model1.predict(np.array([age, sex, cpt, bp, chol, fbp, ecg, mhr, exe_angina, oldpeak, slope]).reshape((1, -1)))
        output = round(prediction1[0])

        user_id = session.get('user_id')
        if user_id:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO heart_combined_results (user_id, age, sex, cpt, bp, chol, fbp, ecg, mhr, exe_angina, oldpeak, slope, prediction)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, age, sex, cpt, bp, chol, fbp, ecg, mhr, exe_angina, oldpeak, slope, output))
            mysql.connection.commit()
            cur.close()

        prediction_message = "No significant risk detected. Maintain your healthy lifestyle." if output == 0 else "Your data indicates a high risk of heart failure. Seek medical attention promptly."

        parameters = {
            'Age': (age, (0, 100)),
            'Sex': (sex, (0, 1)),
            'Chest Pain Type': (cpt, (0, 3)),
            'Blood Pressure': (bp, (80, 120)),
            'Cholesterol': (chol, (125, 200)),
            'Fasting Blood Sugar': (fbp, (0, 1)),
            'Resting ECG': (ecg, (0, 2)),
            'Maximum Heart Rate': (mhr, (60, 220 - age)),
            'Exercise Induced Angina': (exe_angina, (0, 1)),
            'Oldpeak': (oldpeak, (0, 6.2)),
            'Slope': (slope, (1, 3))
        }

        exceeded_parameters = {key: value for key, value in parameters.items() if value[0] < value[1][0] or value[0] > value[1][1]}

        return render_template('result.html', prediction=prediction_message, exceeded_parameters=exceeded_parameters)
    else:
        return render_template('heartcombined.html')





@app.route('/diabetespred', methods=['GET', 'POST'])
def diabetespred():
    if request.method == 'POST':
        pregnancies = int(request.form['Pregnancies'])
        glucose = float(request.form['Glucose'])
        blood_pressure = float(request.form['BloodPressure'])
        skin_thickness = float(request.form['Skinthickness'])
        insulin = float(request.form['Insulin'])
        bmi = float(request.form['BMI'])
        diabetes_pedigree_function = float(request.form['DiabetesPedigreeFunction'])
        age = int(request.form['Age'])

        prediction2 = model2.predict(np.array([pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, diabetes_pedigree_function, age]).reshape((1, -1)))
        output = round(prediction2[0])

        user_id = session.get('user_id')
        if user_id:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO diabetes_results (user_id, pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, diabetes_pedigree_function, age, prediction)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, diabetes_pedigree_function, age, output))
            mysql.connection.commit()
            cur.close()

        prediction_message = "No significant risk detected. Maintain your healthy lifestyle." if output == 0 else "Your data indicates a high risk of heart diabetes. Seek medical attention promptly."

        # Create a dictionary of user parameters and their limits
        parameters = {
            'Pregnancies': (pregnancies, (0, 10)),
            'Glucose': (glucose, (70, 140)),
            'Blood Pressure': (blood_pressure, (80, 120)),
            'Skin Thickness': (skin_thickness, (10, 50)),
            'Insulin': (insulin, (16, 166)),
            'BMI': (bmi, (18.5, 24.9)),
            'Diabetes Pedigree Function': (diabetes_pedigree_function, (0.0, 2.5)),
        }

        # Filter parameters that exceed the limits
        exceeded_parameters = {key: value for key, value in parameters.items() if value[0] < value[1][0] or value[0] > value[1][1]}

        return render_template('result.html', prediction=prediction_message, exceeded_parameters=exceeded_parameters)
    else:
        return render_template('diabetes.html')



if __name__ == "__main__":
   app.run(host='0.0.0.0',port=5000,debug=True)




