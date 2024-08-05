from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/main')
def main():
    id = request.args.get('id')
    if not login():
        return render_template('main.html')
    else:
        return render_template('main.html', id=id)

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == 'POST':
        id = request.form['id']
        pw = request.form['pw']
        school = request.form['school']
        name = request.form['name']

        conn = pymysql.connect(host="127.0.0.1", user="root", password="root", db="signupdb", charset="utf8")
        cursor = conn.cursor()

        SQL1 = "SELECT id FROM signup WHERE id = %s"
        cursor.execute(SQL1, (id))
        result = cursor.fetchone()
        if result:
            flash('중복되는 아이디가 있습니다. 다른 아이디를 사용해주세요.')
            return redirect(url_for('signup'))

        SQL2 = "INSERT INTO signup (id, pw, school, name) VALUES (%s, %s, %s, %s)"
        cursor.execute(SQL2, (id, pw, school, name))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('main'))
    return render_template('signup.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        id = request.form['id']
        pw = request.form['pw']

        conn = pymysql.connect(host="127.0.0.1", user="root", password="root", db="signupdb", charset="utf8")
        cursor = conn.cursor()

        SQL = "SELECT * FROM signup WHERE id = %s AND pw = %s"
        cursor.execute(SQL, (id, pw))
        info = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        if info:
            session['id'] = id
            return redirect(url_for('main', id=id))
        else:
            flash('로그인 실패. 아이디와 비밀번호를 확인하세요.')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('id', None)
    return redirect(url_for('main'))

@app.route('/profile')
def profile():
    id = session.get('id')
    if not id:
        return redirect(url_for('login'))
    
    conn = pymysql.connect(host="127.0.0.1", user="root", password="root", db="signupdb", charset="utf8")
    cursor = conn.cursor()

    SQL = "SELECT id, pw, school, name FROM signup WHERE id = %s"
    cursor.execute(SQL, (id,))
    info = cursor.fetchone()
    cursor.close()
    conn.close()

    if info:
        return render_template('profile.html', info=info)
    else:
        return redirect(url_for('login'))

@app.route('/notice')
def notice():
    id = session.get('id')
    if id:
        conn = pymysql.connect(host="127.0.0.1", user="root", password="root", db="signupdb", charset="utf8")
        cursor = conn.cursor()

        SQL = "SELECT * FROM notice"
        cursor.execute(SQL)
        posts = cursor.fetchall()

        SQL = "SELECT id, pw, school, name FROM signup WHERE id = %s"
        cursor.execute(SQL, (id,))
        info = cursor.fetchone()

        cursor.close()
        conn.close()

        return render_template('notice.html', posts=posts, info=info)
    else:
        return redirect(url_for('login'))

@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']

        conn = pymysql.connect(host="127.0.0.1", user="root", password="root", db="signupdb", charset="utf8")
        cursor = conn.cursor()

        sql = "INSERT INTO notice (title, text) VALUES (%s, %s)"
        cursor.execute(sql, (title, text))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('notice'))
    
    return render_template('write.html')

@app.route('/delete/<title>', methods=['DELETE'])
def delete_post(title):
    conn = pymysql.connect(host="127.0.0.1", user="root", password="root", db="signupdb", charset="utf8")
    cursor = conn.cursor()

    SQL = "DELETE FROM notice WHERE title = %s"
    cursor.execute(SQL, (title,))
    conn.commit()
    
    cursor.close()
    conn.close()

    return '게시물이 삭제되었습니다.', 200

@app.route('/users')
def users():
    conn = pymysql.connect(host="127.0.0.1", user="root", password="root", db="signupdb", charset="utf8")
    cursor = conn.cursor()

    SQL = "SELECT * FROM signup"
    cursor.execute(SQL)
    users_data = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('users.html', users_data=users_data)

if __name__ == '__main__':
    app.run(debug=True)
