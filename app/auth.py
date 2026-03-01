import re
from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from . import db

auth = Blueprint('auth', __name__)

# ==========================
# VALIDATION PATTERNS
# ==========================
NAME_REGEX = r'^[A-Za-z ]{3,}$'
EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'
PASSWORD_REGEX = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'


# ==========================
# LOGIN
# ==========================
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            flash('Login successful!', 'success')

            if user.role == 'doctor':
                return redirect(url_for('main.doctor_dashboard'))
            return redirect(url_for('main.patient_dashboard'))

        else:
            flash('Invalid email or password', 'danger')

    return render_template('auth/login.html')


# ==========================
# SIGNUP
# ==========================
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name').strip()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        role = request.form.get('role')  # 'patient' or 'doctor'

        # -------- Validate Name --------
        if not re.match(NAME_REGEX, name):
            flash('Name must be at least 3 characters and contain only letters.', 'danger')
            return redirect(url_for('auth.signup'))

        # -------- Validate Email --------
        if not re.match(EMAIL_REGEX, email):
            flash('Please enter a valid email address.', 'danger')
            return redirect(url_for('auth.signup'))

        # -------- Validate Password --------
        if not re.match(PASSWORD_REGEX, password):
            flash('Password must be minimum 8 characters and include uppercase, lowercase, number and special character.', 'danger')
            return redirect(url_for('auth.signup'))

        # -------- Check Existing Email --------
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists.', 'warning')
            return redirect(url_for('auth.signup'))

        # -------- Create User --------
        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password, method='scrypt'),
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully!', 'success')

        login_user(new_user)

        if role == 'doctor':
            return redirect(url_for('main.doctor_dashboard'))
        return redirect(url_for('main.patient_dashboard'))

    return render_template('auth/signup.html')


# ==========================
# LOGOUT
# ==========================
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('main.home'))