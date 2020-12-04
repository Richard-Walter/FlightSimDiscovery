from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flightsimdiscovery import db, bcrypt
from flightsimdiscovery.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from flightsimdiscovery.models import User, Pois
from flask_login import login_user, current_user, logout_user, login_required
from flightsimdiscovery.users.utitls import save_picture, send_reset_email, get_user_pois_dict_inc_favorites_visited, get_user_favorited_pois, get_user_visited_pois, get_user_flagged_pois, get_user_flightplans

users = Blueprint('users', __name__)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))

    return render_template("register.html", form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    user_pois = None
    print(current_user.id)
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file  # image file is what we defined in our models.py
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()

        flash('Your account has been updated!', 'success')
        # want to redirect instead of render template so a get request is called instead of  post saying form resubmissions
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        # user_pois_with_additional_data = get_user_pois_dict_inc_favorites_visited(current_user.id)
        # print('###### USER POIS ###### ', user_pois_with_additional_data )

    image_file = url_for('static', filename='img/profile_pics/' + current_user.image_file)
    return render_template('account.html', image_file=image_file, form=form)


@users.route("/user_pois", defaults={'user_id': None})
@users.route("/user_pois/<user_id>")
@login_required
def user_pois(user_id):

    if user_id:
        if (current_user.username != 'admin'):
            if (user_id != str(current_user.id)):
                abort(403)
    else:
        user_id = current_user.id
        
    user_pois_with_additional_data = get_user_pois_dict_inc_favorites_visited(user_id, True)
    favorite_pois = get_user_favorited_pois(user_id)
    visited_pois = get_user_visited_pois(user_id)
    flagged_pois = get_user_flagged_pois(user_id)
    user_flightplan_data = get_user_flightplans(user_id)

    return render_template('user_pois.html', user_pois=user_pois_with_additional_data, favorite_pois=favorite_pois, visited_pois=visited_pois, flagged_pois=flagged_pois, user_flightplan_data=user_flightplan_data)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', form=form)
