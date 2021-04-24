## pip instal flask
from flask import Flask, request, render_template, session, redirect, flash
## pip install Flask-SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
## pip install Flask-Login
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# Password Hash 
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users\shari\Documents\Chronic-Illness-Self-Help-Portal\chronic.db'
app.config['SECRET_KEY'] = 'SECRET_KEY_INPUT'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

### OUR DB CLASSES
class User_info(UserMixin, db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    gender = db.Column(db.Integer)
    email = db.Column(db.String(60), unique=True)
    password = db.Column(db.String(100))
    account_type = db.Column(db.Integer)
    account_info = db.Column(db.Integer)
    ###### relationship ######
    patient = db.relationship('Patient', backref='User_info', uselist=False)
    provider = db.relationship('Provider', backref='User_info', uselist=False)
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_info_id=db.Column(db.Integer, db.ForeignKey('user_info.id'), unique=True)
    dob = db.Column(db.String(12))
    country = db.Column(db.String(30))
    chronic_illness_name = db.Column(db.String(60))
    chronic_illness_category = db.Column(db.String(60))
class Provider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_info_id=db.Column(db.Integer, db.ForeignKey('user_info.id'), unique=True)
    serving_as = db.Column(db.String(60))
class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider_name = db.Column(db.String(60))
    illness = db.Column(db.String(30))
    notes_text = db.Column(db.String(225))
    date = db.Column(db.String(12))
    provider_categroy = db.Column(db.String(60))
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notification = db.Column(db.String(100))
    chronic_illness_name = db.Column(db.String(60))
    date = db.Column(db.String(12))
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider_name = db.Column(db.String(100))
    patient_name = db.Column(db.String(80))
    appointment_date_time = db.Column(db.String(30))
    appointment_for = db.Column(db.String(225))

## Login Manager Function/load_user function 
@login_manager.user_loader
def load_user(user_id):
    return User_info.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    if current_user.is_authenticated:
        return redirect('/dashboard')
    else: 
        return render_template('login.html')

################################## LOGIN, LOGOUT & SIGNUP ################################## 

#TODO: LOGIN
@app.route('/login', methods = ['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        # try:
        user = User_info.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
              login_user(user)
              return redirect('/dashboard')  
        else:
            flash('Email Does not Exist or Password incorrect!')
            return render_template('login.html')
    else: 
        return render_template('login.html')

#TODO: SIGNUP
@app.route('/signup', methods = ['GET','POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        account_type = request.form['account_type']
        account_info = request.form['account_info']

        new_user_info = User_info(first_name=first_name, last_name=last_name, gender=gender, email=email, password=generate_password_hash(password), account_type=account_type,account_info=account_info)
        db.session.add(new_user_info)
        try:
            db.session.commit()
            return render_template('login.html')            
        except IntegrityError:
            flash('Email Already Taken')
            db.session.rollback()
            return render_template('register.html')
        return render_template('login.html')

    return render_template('register.html')

# TODO: Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('login.html')


################################## END LOGIN , LOGOUT & SIGNUP ################################## 

@app.route('/dashboard', methods = ['GET','POST'])
@login_required
def dashboard():
    if current_user.account_info == 0:
        if current_user.account_type == 'Patient':
            return render_template('profile.html')
        elif current_user.account_type == 'Provider':   
            return render_template('provider_profile.html')   
    else:
        if current_user.account_type == 'Patient':
            notes = Notes.query.filter_by(illness=current_user.patient.chronic_illness_name)
            return render_template('dashboard.html', notes=notes)
        elif current_user.account_type == 'Provider':   
            provider_name = current_user.first_name + ' ' +current_user.last_name
            notes = Notes.query.filter_by(provider_name=provider_name)
            return render_template('provider_dashboard.html', notes=notes)
    # return render_template('login.html')
    return redirect('/login')

################################## Notification ################################## 
@app.route('/notify', methods = ['GET','POST'])
@login_required
def notify():
    notifications = Notification.query.filter_by(chronic_illness_name=current_user.patient.chronic_illness_name)
    return render_template('notify.html', notifications=notifications)
################################## End Notification ##################################
 
@app.route('/profile', methods = ['GET','POST'])
@login_required
def profile():
    if current_user.account_info == 0:
        if current_user.account_type == 'Patient':
            if request.method == 'POST':
                dob = request.form['dob']
                country = request.form['country']
                chronic_illness_name = request.form['chronic_illness_name']
                chronic_illness_category = request.form['chronic_illness_category']
                user_info_id = request.form['user_info_id']
                
                user = User_info.query.filter_by(id=current_user.id).first()
                user.account_info = 1
                patient_profile = Patient(user_info_id=user_info_id, dob=dob,country=country,chronic_illness_name=chronic_illness_name, chronic_illness_category=chronic_illness_category)

                # db.session.add(user)
                db.session.add(patient_profile)
                db.session.commit()

                return redirect('/dashboard')
            return render_template('profile.html')
        elif current_user.account_type == 'Provider':
            if request.method == 'POST':
                serving_as = request.form['serving_as']
                user_info_id = request.form['user_info_id']
                
                user = User_info.query.filter_by(id=current_user.id).first()
                user.account_info = 2
                provider = Provider(user_info_id=user_info_id, serving_as=serving_as)

                db.session.add(provider)
                db.session.commit()

                return redirect('/dashboard')
            return render_template('profile.html')

    else:
        return render_template('dashboard.html')

################################## Notes ################################## 
# TODO: SHOW NOTES
@app.route('/notes', methods = ['GET','POST'])
@login_required
def notes():
    if current_user.account_info == 0 and current_user.account_type == 'Patient':
        return render_template('profile.html')
    elif current_user.account_info == 0 and current_user.account_type == 'Provider':   
        return render_template('provider_profile.html')           
    elif current_user.account_info == 2 and current_user.account_type == 'Provider':
        provider_name = current_user.first_name + ' ' +current_user.last_name
        notes = Notes.query.filter_by(provider_name=provider_name)
        return render_template('provider_notes.html', notes=notes)
    elif current_user.account_info == 1 and current_user.account_type == 'Patient':
        return render_template('dashboard.html')
        
    return render_template('login.html')

# TODO: ADD Notes
@app.route('/add-notes', methods = ['GET','POST'])
@login_required
def add_notes():
    if current_user.account_info == 2 and current_user.account_type == 'Provider':
        if request.method == 'POST':
            illness = request.form['illness']
            notes_text = request.form['notes_text']
            date = datetime.now()
            provider_name = current_user.first_name + ' ' +current_user.last_name
            notes = Notes(provider_name=provider_name, illness=illness, notes_text=notes_text, date=date.strftime("%d/%m/%y"), provider_categroy=current_user.provider.serving_as)
            db.session.add(notes)
            db.session.commit()
            flash('Note Added Successfully!','success')    
            return redirect('/notes')
        else:
            return 'SOME ERROR'   
    else:
        return 'NOT ALLOWED'        

# TODO: Update Notes
@app.route('/update-notes', methods = ['GET','POST'])
@login_required
def update_notes():
    if current_user.account_info == 2 and current_user.account_type == 'Provider':
        if request.method == 'POST':
            data_id = request.form['data_id']
            data_date = request.form['data_date']
            data_illness = request.form['data_illness']
            data_notes_text = request.form['data_notes_text']
             
            notes = Notes.query.filter_by(id=data_id).first()
            notes.illness = data_illness
            notes.notes_text =data_notes_text
            notes.date = data_date
            db.session.add(notes)
            db.session.commit()
            flash('Updated Successfully!','warning')    
            return redirect('/notes')
        else:
            return 'SOME ERROR'   
    else:
        return 'NOT ALLOWED'           

# TODO: DELETE NOTES
@app.route('/delete-notes/<string:id>', methods = ['GET','POST'])
@login_required
def delete_notes(id):
    if current_user.account_info == 2 and current_user.account_type == 'Provider':
        notes = Notes.query.filter_by(id=id).first()
        db.session.delete(notes)

        db.session.commit()
        flash('Row Deleted!', 'danger')
        return redirect('/notes')
    else:
        return 'NOT ALLOWED'        

################################## End Notes ##################################

################################## Patients List ##################################
# TODO: SHOW Patients List
@app.route('/patients-list')
@login_required
def patients_list():
    if current_user.account_info == 2 and current_user.account_type == 'Provider':
        patients = User_info.query.filter_by(account_type='Patient')
        
        return render_template('provider_patient_list.html' , patients=patients)
    else:
        return 'NOT ALLOWED'           

################################## End Patients List ##################################

@app.route('/forget-password')
def forget_password():
    return render_template('forget_password.html')    

################################## Virtual Appintement ##################################
@app.route('/virtual-apppointments')
@login_required
def virtual_apppointment():
    if current_user.account_info == 1 and current_user.account_type == 'Patient':
        providers = User_info.query.filter_by(account_type='Provider')
        patient_name = current_user.first_name + ' ' +current_user.last_name
        appointments = Appointment.query.filter_by(patient_name=patient_name)
        return render_template('virtual_appointments.html', providers=providers, appointments=appointments)
      
    else:
        return 'NOT ALLOWED'  

@app.route('/book-apppointment', methods = ['GET','POST'])
@login_required
def book_apppointment():
    if current_user.account_info == 1 and current_user.account_type == 'Patient':
        if request.method == 'POST':
            provider_name = request.form['provider_name'] 
            appointment_date_time = request.form['appointment_date_time']
            appointment_for = request.form['appointment_for']
            patient_name = current_user.first_name + ' ' + current_user.last_name
            appointment = Appointment(provider_name=provider_name, patient_name=patient_name, appointment_date_time=appointment_date_time, appointment_for=appointment_for)
            db.session.add(appointment)
            db.session.commit()
            return redirect('/virtual-apppointments')
        else:
            return 'SOME ERROR'   
    else:
        return 'NOT ALLOWED'  

################################## End Virtual Appintement ##################################

################################## Diet Suppliment ##################################

@app.route('/diet-suppliment')
def diet_suppliment():
    if current_user.account_info == 1 and current_user.account_type == 'Patient':
        return render_template('diet-suppliment.html')
    else:
        return 'NOT ALLOWED'    

################################## End Diet Suppliment ##################################

################################## Media Center ##################################

@app.route('/media-center')
@login_required
def media_center():
    if current_user.account_info == 1 and current_user.account_type == 'Patient':
        return render_template('media_center.html')
    else:
        return 'NOT ALLOWED'    

################################## End Media Center ##################################


################################## Information Hub ##################################

@app.route('/information-hub')
@login_required
def information_hub():
    if current_user.account_info == 1 and current_user.account_type == 'Patient':
        return render_template('information_hub.html')    
    else:
        return 'NOT ALLOWED'

################################## End Information Hub ##################################

################################## Counselling  ##################################
@app.route('/counselling')
@login_required
def counselling():
    if current_user.account_info == 1 and current_user.account_type == 'Patient':
        return render_template('counselling.html')
    else:
        return 'NOT ALLOWED'
################################## End Counselling ##################################


if __name__ == '__main__':
    app.run(debug=True)