# auth.py

from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from models import User
from __init__ import get_db_connection, db

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template('login.html', title="Авторизация")


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('Пожалуйста, проверьте вводимые данные.')
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))


@auth.route('/signup')
def signup():
    return render_template('signup.html', title="Регистрация")


@auth.route('/signup', methods=['POST'])
def signup_post():
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        patr = request.form.get('patr')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email address already exists')
            return redirect(url_for('auth.signup'))

        new_user = User(email=email, name=name, surname=surname,
                        password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO Client (Surname,Name,Patronymic,Email,Password,Phone)'
                    'VALUES (%s, %s, %s, %s, %s, %s)',
                    (surname, name, patr, email, password, phone))

        # Пофиксить следующую строку:
        cur.execute('INSERT INTO Briefcase (Shares_ID, Amount)'
                    'VALUES (%s, %s)',
                    (2, 1))

        cur.execute('SELECT * FROM Client;')
        Client = cur.fetchall()
        cur.execute('SELECT * FROM Briefcase;')
        Briefcase = cur.fetchall()
        for cl in Client:
            for BC in Briefcase:
                if email == cl[4]:
                    ClId = cl[0]
                    BCid = BC[0]

        cur.execute('INSERT INTO Bankaccount (RUB,USD,Client_ID, Briefcase_ID)'
                    'VALUES (%s, %s, %s, %s)',
                    (0, 0, ClId, BCid))

        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('main.index'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
