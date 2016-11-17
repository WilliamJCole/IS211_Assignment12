#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Assignment 12 docstring."""


import sqlite3
import sys
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash


DATABASE = './hw12.db'
DEBUG = True
SECRET_KEY = 'secret key'
USERNAME = 'admin'
PASSWORD = 'password'


app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/', methods=['GET'])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    return redirect(url_for('show_entries'))


@app.route('/dashboard', methods=['GET', 'POST'])
def show_entries():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    cur = g.db.execute('select student_id, first_name, last_name \
                       from students order by student_id asc')
    students = [dict(ID=row[0], fname=row[1], lname=row[2])
                for row in cur.fetchall()]

    cur = g.db.execute('select quizz_id, subject, questions, date \
                       from quizzes order by quizz_id asc')
    quizzes = [dict(ID=row[0], subject=row[1], questions=row[2], date=row[3])
               for row in cur.fetchall()]

    return render_template('show_entries.html', students=students, quizzes=quizzes)


@app.route('/student/<id>', methods=['GET'])
def show_student(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    cur = g.db.execute('SELECT students.first_name, students.last_name, \
                    quizzes.subject, quizzes.questions, quizzes.date, results.score \
                    FROM students \
                    LEFT JOIN results \
                    ON results.student_id  = students.student_id \
                    LEFT JOIN quizzes \
                    ON results.quizz_id = quizzes.quizz_id \
                    WHERE students.student_id = {};'.format(id))

    student = [dict(fname=row[0], lname=row[1], subject=row[2], questions=row[3],
                    date=row[4], score=row[5]) for row in cur.fetchall()]

    return render_template('show_student.html', student=student)


@app.route('/student/add', methods=['GET', 'POST'])
def add_student():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    return render_template('add_student.html')


@app.route('/student/insert', methods=['GET', 'POST'])
def insert_student():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    try:
        g.db.execute('insert into students (first_name, last_name) values (?, ?)',
                 [request.form['fname'], request.form['lname']])
        g.db.commit()
        flash('New entry was successfully posted')

        return redirect(url_for('show_entries'))
    except:
        return redirect(url_for('add_student'))


@app.route('/quiz/add', methods=['GET', 'POST'])
def add_quiz():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    return render_template('add_quiz.html')


@app.route('/quiz/insert', methods=['GET', 'POST'])
def inset_quiz():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        g.db.execute('insert into quizzes (subject, questions, date) values (?, ?, ?)',
                 [request.form['subject'], request.form['questions'], request.form['date']])
        g.db.commit()
        flash('New quiz entry was successfully posted')

        return redirect(url_for('show_entries'))
    except:
        e = sys.exc_info()[0]
        print e
        return redirect(url_for('add_quiz'))


@app.route('/results/add', methods=['GET', 'POST'])
def add_results():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    cur = g.db.execute('select student_id, first_name, last_name \
                       from students order by student_id asc')
    students = [dict(ID=row[0], fname=row[1], lname=row[2])
                for row in cur.fetchall()]

    cur = g.db.execute('select quizz_id, subject, questions, date \
                       from quizzes order by quizz_id asc')
    quizzes = [dict(ID=row[0], subject=row[1]) for row in cur.fetchall()]

    return render_template('add_results.html', students=students, quizzes=quizzes)


@app.route('/results/insert', methods=['GET', 'POST'])
def insert_results():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        g.db.execute('insert into results (student_id, quizz_id, score) values (?, ?, ?)',
                 [request.form['student'], request.form['quiz'], request.form['score']])
        g.db.commit()
        flash('New score entry was successfully posted')

        return redirect(url_for('show_entries'))
    except:
        e = sys.exc_info()[0]
        print e
        return redirect(url_for('add_results'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if 'username' in session:
        return redirect(url_for('show_entries'))
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')

    return redirect(url_for('index'))

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == '__main__':
    app.run()
