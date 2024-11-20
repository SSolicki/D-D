from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, current_user
from app import db, cache, limiter
from app.auth import bp
from app.models import User
from app.auth.forms import LoginForm, RegistrationForm
from werkzeug.urls import url_parse

@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("20 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("10 per hour")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User()
            user.username = form.username.data
            user.email = form.email.data
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Congratulations, you are now a registered user!', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error during registration. Please try again.', 'error')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/check_username/<username>')
@limiter.limit("30 per minute")
def check_username(username):
    user = User.query.filter_by(username=username).first()
    return jsonify({'available': user is None})

@bp.route('/check_email/<email>')
@limiter.limit("30 per minute")
def check_email(email):
    user = User.query.filter_by(email=email).first()
    return jsonify({'available': user is None})
