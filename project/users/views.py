from flask import flash, redirect, render_template, url_for, request, Blueprint
from project.users.forms import LoginForm
from project.models import User, db
from flask_login import login_user, login_required, logout_user
from ldap import INVALID_CREDENTIALS, SERVER_DOWN
from sqlalchemy.exc import OperationalError, ProgrammingError
import os


users_blueprint = Blueprint('users', __name__, template_folder='templates')


@users_blueprint.route('/', methods=['GET'])
def main_page():
    return redirect(url_for('operator.new_network'))


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
            username = username.split('@')[0]

            # ldap login
            try:
                # making some orderings so as to accept both DOMAIN\USER, USER at login
                ad_domain = os.environ['USERDNSDOMAIN'].lower().split(".")[0]
                username = username.split("\\")[-1]
                ldap_username = ad_domain + "\\" + username

                ldap_login_user = User.ldap_login(ldap_username, password)
                if ldap_login_user:
                    # verify if the user exists in DB and besides if DB is working!!
                    try:
                        user = User.query.filter_by(username=username).first()
                    except (ProgrammingError, OperationalError) as e:
                        error = str(e)
                        return render_template('login.html', form=form, error=error)

                    if not user:
                        email_suffix = ad_domain + ".com"
                        email = username + "@" + email_suffix
                        try:
                            name, surname = username.split('.')
                        except ValueError:
                            name = username
                            surname = 'service_user'
                        password = 'auth-by-ldap-eiaxzqnO4JKUwsQ'
                        users_exist = User.query.all()
                        # first user who logs in is going to be admin
                        if users_exist:
                            user = User(username, password, email, name, surname)
                        else:
                            user = User(username, password, email, name, surname, admin=True, operator=True)
                        db.session.add(user)
                        db.session.commit()
                    login_user(user)  # (flask_login) session created
                    return redirect(url_for('operator.new_network'))

            except INVALID_CREDENTIALS:
                error = 'Invalid Credentials. Please try again.'
            except SERVER_DOWN:
                error = 'Authentication Server Unreachable'

    return render_template('login.html', form=form, error=error, current_user=False)


@users_blueprint.route('/logout')
@login_required  # flask_login
def logout():
    logout_user()  # (flask_login) clear session
    flash('You are logged out.')
    return redirect(url_for('users.login'))


@users_blueprint.route('/err_403')
def err_403():
    return render_template('403.html', title='403')
