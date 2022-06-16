from flask import Blueprint, Flask, render_template, request, url_for, redirect, flash
from flask_login import login_user, logout_user, login_required, LoginManager, current_user
from __init__ import create_app, db, get_db_connection

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/shares')
def shares():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Shares;')
    Shares = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('shares.html', Shares=Shares)


@main.route('/shares', methods=['POST'])
@login_required
def shares_post():

    name = request.form.get('name')
    ticker = request.form.get('ticker')
    price = request.form.get('price')
    descript = request.form.get('descript')
    issuer = '-'
    count = request.form.get('count')
    print(count)
    if request.form.get('check'):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO Shares (Name,Ticker,Issuer,Price,Descript)'
                    'VALUES (%s, %s, %s, %s, %s)',
                    (name, ticker, issuer, price, descript))

        conn.commit()
        cur.close()
        conn.close()

    return redirect(url_for('main.shares'))


@main.route('/profile')
@login_required
def profile():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT c.id, ba.id, ba.rub, ba.usd FROM Client AS c, BankAccount AS ba WHERE c.Email = %s and c.id = '
                'ba.client_id', [current_user.email])
    Data = cur.fetchall()
    cur.execute('SELECT sh.name, sh.ticker, sh.price, bc.amount, sh.price * bc.amount AS total_price FROM Client AS '
                'c, Shares AS sh, Briefcase AS bc, BankAccount AS ba WHERE ba.Client_ID = c.id and ba.Briefcase_ID = '
                'bc.id and bc.Shares_ID = sh.id and c.email = %s;', [current_user.email])
    ClShares = cur.fetchall()

    conn.commit()
    cur.close()
    conn.close()

    return render_template('profile.html', name=current_user.name, surname=current_user.surname, ClShares=ClShares,
                           Data=Data)


@main.route('/profile', methods=['POST'])
@login_required
def profile_post():
    rub = int(request.form.get('rub'))
    usd = int(request.form.get('usd'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT c.id, ba.id, ba.rub, ba.usd FROM Client AS c, BankAccount AS ba WHERE c.Email = %s and c.id = '
                'ba.client_id', [current_user.email])
    Data = cur.fetchall()

    for data in Data:
        if rub != 0:
            cur.execute('UPDATE BankAccount SET RUB = RUB + %s WHERE id = %s;',
                        (rub, data[1]))
        if usd != 0:
            cur.execute('UPDATE BankAccount SET USD = USD + %s WHERE id = %s;',
                        (usd, data[1]))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('main.profile'))


if __name__ == '__main__':
    # Не забудь закомментить следующую строчку:
    # db.create_all(app=create_app())
    create_app().run(debug=True)
