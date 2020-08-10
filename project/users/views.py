from flask import flash, redirect, render_template, url_for, request, Blueprint
from project.users.forms import LoginForm
from project.models import User, db
from flask_login import login_user, login_required, logout_user


users_blueprint = Blueprint('users', __name__, template_folder='templates')


# login page
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    error = None
    if request.method == 'POST':
        if form.validate_on_submit():
            # user = User.query.filter_by(username=request.form['username']).first()
            username = request.form['username']
            password = request.form['password']

            # if user is not None and bcrypt.check_password_hash(user.password, request.form['password']):
            # if user is not None and bcrypt.check_password_hash(user.password, request.form['password']):
            print(User.ldap_login(username, password))
            if User.ldap_login(username, password):
                user = User.query.filter_by(email=username).first()
                if not user:
                    email = username
                    username = username.split('@')[0]
                    try:
                        name, surname = username.split('.')
                    except ValueError:
                        name = username
                        surname = 'service_user'
                    password = 'auth-by-ldap-eiaxzqnO4JKUwsQ'
                    user = User(username, password, email, name, surname)
                    db.session.add(user)
                    db.session.commit()
                login_user(user)  # (flask_login) session created
                flash('You are logged in.')
                return redirect(url_for('home.home'))
            else:
                error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', form=form, error=error)


@users_blueprint.route('/logout')
@login_required  # flask_login
def logout():
    logout_user()  # (flask_login) clear session
    flash('You are logged out.')
    return redirect(url_for('home.welcome'))
