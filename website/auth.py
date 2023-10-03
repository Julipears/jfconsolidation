# copied from views.py
# stores standard routes for website
# ie. where users can go to 
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db       # means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)
loggedIn = False

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Login Successful', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home')) #views.user_info after it has been implemented
            else:
                flash('Incorrect password', category='error')
                email = request.form.get('email')
        else:
            flash('Email does not exist', category='error')
    # request stores information sent in form
    data = request.form
    print(data)
        # returns some HTML for /login to render
    # render_template("login.html") fetches the HTML as a template
    # second arg: define any variable; can be used anywhere within login.html template
    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
        # request stores information sent in form
    data = request.form
    print(data)

    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists', category='error')


            # base.html will actually show flash messages
        if len(email) < 4:
            flash('Email must be greater than 4 characters', category='error')
        elif len(first_name) < 2:
            flash('Name is too short', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)        # add new user to database
            db.session.commit()             # commit changes
            login_user(new_user, remember=True)
            flash('Account created', category='success')
                # format: blueprint_name.function_name
            return redirect(url_for('auth.login'))

    return render_template("signup.html", user=current_user)