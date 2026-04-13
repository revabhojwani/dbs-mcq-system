from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'mcq_dbs_project_2024'

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="your_password",
        database="mcq_system"
    )
    return conn

@app.route('/')
def role_select():
    return render_template("role_select.html")

@app.route('/student_dashboard')
def student_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Student")
    student_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Test")
    test_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Question")
    question_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return render_template("student_dashboard.html",
        student_count=student_count,
        test_count=test_count,
        question_count=question_count)

@app.route('/admin')
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT T.test_id, T.title, T.duration_minutes, A.name
        FROM Test T
        JOIN Administrator A ON T.admin_id = A.admin_id
    """)
    tests = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin.html", tests=tests)

@app.route('/students')
def students():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Student")
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("students.html", students=students)

@app.route('/tests')
def tests():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT T.test_id, T.title, T.duration_minutes, A.name
        FROM Test T
        JOIN Administrator A ON T.admin_id = A.admin_id
    """)
    tests = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("tests.html", tests=tests)

@app.route('/student_tests')
def student_tests():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT T.test_id, T.title, T.duration_minutes, A.name
        FROM Test T
        JOIN Administrator A ON T.admin_id = A.admin_id
    """)
    tests = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("student_tests.html", tests=tests)

@app.route('/test/<int:test_id>')
def view_test(test_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Test WHERE test_id = %s", (test_id,))
    test = cursor.fetchone()
    cursor.execute("SELECT * FROM Question WHERE test_id = %s", (test_id,))
    questions = cursor.fetchall()
    question_data = []
    for question in questions:
        cursor.execute(
            "SELECT option_id, option_text FROM OptionTable WHERE question_id = %s",
            (question[0],))
        options = cursor.fetchall()
        question_data.append({"question": question, "options": options})
    cursor.close()
    conn.close()
    return render_template("view_test.html", test=test, question_data=question_data)

@app.route('/student_test/<int:test_id>')
def student_view_test(test_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Test WHERE test_id = %s", (test_id,))
    test = cursor.fetchone()
    cursor.execute("SELECT * FROM Question WHERE test_id = %s", (test_id,))
    questions = cursor.fetchall()
    question_data = []
    for question in questions:
        cursor.execute(
            "SELECT option_id, option_text FROM OptionTable WHERE question_id = %s",
            (question[0],))
        options = cursor.fetchall()
        question_data.append({"question": question, "options": options})
    cursor.close()
    conn.close()
    return render_template("student_view_test.html", test=test, question_data=question_data)

@app.route('/attempt/<int:test_id>')
def attempt_test(test_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Test WHERE test_id = %s", (test_id,))
    test = cursor.fetchone()
    cursor.execute("SELECT * FROM Student")
    students = cursor.fetchall()
    cursor.execute("SELECT * FROM Question WHERE test_id = %s", (test_id,))
    questions = cursor.fetchall()
    question_data = []
    for question in questions:
        cursor.execute(
            "SELECT option_id, option_text FROM OptionTable WHERE question_id = %s",
            (question[0],))
        options = cursor.fetchall()
        question_data.append({"question": question, "options": options})
    cursor.close()
    conn.close()
    return render_template("attempt_test.html",
        test=test, students=students, question_data=question_data)

@app.route('/submit_test/<int:test_id>', methods=['POST'])
def submit_test(test_id):
    student_id = request.form.get("student_id")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO Attempt (student_id, test_id, score) VALUES (%s, %s, %s)",
        (student_id, test_id, 0)
    )
    attempt_id = cursor.lastrowid

    cursor.execute("SELECT question_id FROM Question WHERE test_id = %s", (test_id,))
    questions = cursor.fetchall()

    for question in questions:
        question_id = question[0]
        selected_option_id = request.form.get(f"question_{question_id}")
        if selected_option_id:
            cursor.execute(
                "INSERT INTO Response (attempt_id, question_id, selected_option_id) VALUES (%s, %s, %s)",
                (attempt_id, question_id, selected_option_id)
            )

    conn.commit()

    cursor.execute("""
        SELECT A.attempt_id, S.name, T.title, A.score, A.attempt_date
        FROM Attempt A
        JOIN Student S ON A.student_id = S.student_id
        JOIN Test T ON A.test_id = T.test_id
        WHERE A.attempt_id = %s
    """, (attempt_id,))
    result = cursor.fetchone()

    cursor.execute(
        "SELECT COALESCE(SUM(marks),0) FROM Question WHERE test_id = %s",
        (test_id,)
    )
    total_marks = cursor.fetchone()[0]

    cursor.execute("""
        SELECT q.question_text,
               sel.option_text AS selected_text,
               sel.is_correct,
               cor.option_text AS correct_text
        FROM Response r
        JOIN Question q ON r.question_id = q.question_id
        JOIN OptionTable sel ON r.selected_option_id = sel.option_id
        JOIN OptionTable cor ON cor.question_id = q.question_id AND cor.is_correct = 1
        WHERE r.attempt_id = %s
    """, (attempt_id,))
    rows = cursor.fetchall()

    breakdown = []
    for row in rows:
        breakdown.append({
            "question_text": row[0],
            "selected_text": row[1],
            "correct": bool(row[2]),
            "correct_text": row[3]
        })

    cursor.close()
    conn.close()
    return render_template("result.html", result=result,
                           total_marks=total_marks, breakdown=breakdown)

@app.route('/add_test', methods=['GET', 'POST'])
def add_test():
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        title = request.form['title']
        duration_minutes = request.form['duration_minutes']
        admin_id = request.form['admin_id']
        cursor.execute(
            "INSERT INTO Test (title, duration_minutes, admin_id) VALUES (%s, %s, %s)",
            (title, duration_minutes, admin_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Test added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    cursor.execute("SELECT * FROM Administrator")
    admins = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("add_test.html", admins=admins)

@app.route('/add_question/<int:test_id>', methods=['GET', 'POST'])
def add_question(test_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        question_text = request.form['question_text']
        marks = request.form['marks']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        correct_option = request.form['correct_option']
        cursor.execute(
            "INSERT INTO Question (test_id, question_text, marks) VALUES (%s, %s, %s)",
            (test_id, question_text, marks)
        )
        question_id = cursor.lastrowid
        options = [option1, option2, option3, option4]
        for i, option_text in enumerate(options, start=1):
            is_correct = 1 if str(i) == correct_option else 0
            cursor.execute(
                "INSERT INTO OptionTable (question_id, option_text, is_correct) VALUES (%s, %s, %s)",
                (question_id, option_text, is_correct)
            )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Question added successfully!', 'success')
        return redirect(url_for('view_test', test_id=test_id))
    cursor.execute("SELECT * FROM Test WHERE test_id = %s", (test_id,))
    test = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("add_question.html", test=test)

@app.route('/delete_test/<int:test_id>')
def delete_test(test_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT question_id FROM Question WHERE test_id = %s", (test_id,))
    questions = cursor.fetchall()
    for question in questions:
        qid = question[0]
        cursor.execute("DELETE FROM Response WHERE question_id = %s", (qid,))
        cursor.execute("DELETE FROM OptionTable WHERE question_id = %s", (qid,))
    cursor.execute("DELETE FROM Attempt WHERE test_id = %s", (test_id,))
    cursor.execute("DELETE FROM Question WHERE test_id = %s", (test_id,))
    cursor.execute("DELETE FROM Test WHERE test_id = %s", (test_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Test deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_question/<int:question_id>/<int:test_id>')
def delete_question(question_id, test_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Response WHERE question_id = %s", (question_id,))
    cursor.execute("DELETE FROM OptionTable WHERE question_id = %s", (question_id,))
    cursor.execute("DELETE FROM Question WHERE question_id = %s", (question_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('view_test', test_id=test_id))

@app.route('/student_report/<int:student_id>')
def student_report(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Student WHERE student_id = %s", (student_id,))
    student = cursor.fetchone()
    cursor.callproc('GetStudentReport', [student_id])
    report = []
    for result in cursor.stored_results():
        report = result.fetchall()
    cursor.close()
    conn.close()
    return render_template("student_report.html", student=student, report=report)

@app.route('/analytics')
def analytics():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.title,
               COUNT(a.attempt_id) AS attempts,
               COALESCE(AVG(a.score), 0) AS avg_score,
               COALESCE(MAX(a.score), 0) AS top_score
        FROM Test t
        LEFT JOIN Attempt a ON t.test_id = a.test_id
        GROUP BY t.test_id, t.title
    """)
    test_stats = cursor.fetchall()
    cursor.execute("""
        SELECT s.name, t.title, a.score
        FROM Attempt a
        JOIN Student s ON a.student_id = s.student_id
        JOIN Test t ON a.test_id = t.test_id
        WHERE a.score = (
            SELECT MAX(a2.score) FROM Attempt a2 WHERE a2.test_id = a.test_id
        )
    """)
    top_scorers = cursor.fetchall()
    cursor.execute("""
        SELECT name FROM Student
        WHERE student_id NOT IN (SELECT DISTINCT student_id FROM Attempt)
    """)
    not_attempted = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("analytics.html",
        test_stats=test_stats,
        top_scorers=top_scorers,
        not_attempted=not_attempted)

if __name__ == '__main__':
    app.run(debug=True)