from flask import flash, redirect, render_template, url_for, request, Blueprint
from project.users.forms import LoginForm
from project.models import User, db
from flask_login import login_user, login_required, logout_user, current_user
from ldap import INVALID_CREDENTIALS, SERVER_DOWN
from sqlalchemy.exc import OperationalError, ProgrammingError
from project.logging import send_wr_log
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
            input_username = request.form['username']
            password = request.form['password']

            # if user is not None and bcrypt.check_password_hash(user.password, request.form['password']):
            username = input_username.split('@')[0]

            # making some orderings so as to accept both DOMAIN\USER, USER at login
            ad_domain = os.environ['USERDNSDOMAIN'].lower().split(".")[0]
            username = username.split("\\")[-1]
            ldap_username = ad_domain + "\\" + username

            # ldap login
            try:
                ldap_login_user = User.ldap_login(ldap_username, password)
                if ldap_login_user:
                    log_msg = "Authentication Success against LDAP: {}".format(ldap_username)
                    send_wr_log(log_msg)
                    # verify if the user exists in DB and besides if DB is working!!
                    try:
                        user = User.query.filter_by(username=username).first()
                    except (ProgrammingError, OperationalError) as e:
                        error = str(e)
                        log_msg = "Database error on login: {}".format(error)
                        send_wr_log(log_msg)
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
                    log_msg = "User logged in: {}".format(current_user.username)
                    send_wr_log(log_msg)

                    if current_user.operator:
                        return redirect(url_for('operator.new_network'))
                    elif current_user.admin:
                        return redirect(url_for('admin.admin_users'))
                    else:
                        return render_template('403.html', title='403'), 403


            except INVALID_CREDENTIALS:
                error = 'Invalid Credentials. Please try again.'
                log_msg = "Authentication Failure: {}: {}".format(ldap_username, error)
                send_wr_log(log_msg)
            except SERVER_DOWN:
                error = 'Authentication Server Unreachable'
                send_wr_log("Login attempt: {}".format(error))

    return render_template('login.html', form=form, error=error, current_user=False)


@users_blueprint.route('/logout')
@login_required  # flask_login
def logout():
    log_msg = "User logged out: {}".format(current_user.username)
    send_wr_log(log_msg)
    logout_user()  # (flask_login) clear session
    flash('You are logged out.')
    return redirect(url_for('users.login'))


@users_blueprint.route('/err_403')
def err_403():
    return render_template('403.html', title='403')
