from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models.pengguna import Pengguna
from flask_bcrypt import Bcrypt
from datetime import date
from app.forms import RegisterForm, LoginForm


bp = Blueprint('auth', __name__, url_prefix='/auth')
bcrypt = Bcrypt()


@bp.record_once
def on_load(state):
    # initialize bcrypt with app context when blueprint is registered
    bcrypt.init_app(state.app)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        existing = Pengguna.query.filter_by(EMAIL=email).first()
        if existing:
            flash('Email sudah digunakan.')
            return redirect(url_for('auth.register'))
        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = Pengguna(USERNAME=username, EMAIL=email, PASSWORD=pw_hash, TANGGAL_DAFTAR=date.today())
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.ID_PENGGUNA
        session['is_onboarded'] = bool(user.IS_ONBOARDED)
        return redirect(url_for('onboarding.index'))
    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = Pengguna.query.filter_by(EMAIL=email).first()
        if not user or not bcrypt.check_password_hash(user.PASSWORD, password):
            flash('Email atau password salah.')
            return redirect(url_for('auth.login'))
        session['user_id'] = user.ID_PENGGUNA
        session['is_onboarded'] = bool(user.IS_ONBOARDED)
        return redirect(url_for('rekomendasi.home'))
    return render_template('auth/login.html', form=form)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
