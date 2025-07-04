from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, User, Note
import pymysql

def getConnection():
    return pymysql.connect(
        host='localhost',
        db='ai_note',
        user='note_User',
        password='NOTE-uSER',
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
    )

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_required
def index():
    return render_template('index.html', name=current_user.user_id)

orders = ["新しい順", "古い順"]

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(user_id=user_id).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('ログイン情報が正しくありません。')
    return render_template('login.html')

@app.route('/logout')

@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/", methods=["GET", "POST"])
def index():
    connection = getConnection()
    cursor = connection.cursor()
    sql = "SELECT * FROM notes"
    cursor.execute(sql)
    notes = cursor.fetchall()

    searchword = ""
    order = "新しい順"

    if request.method == "POST":
        searchword = request.form.get("searchword")
        order = request.form.get('order')
    
    if searchword:
        if order == "新しい順":
            sql = "SELECT * FROM notes WHERE title LIKE %s OR content LIKE %s ORDER BY update_time DESC"
            cursor.execute(sql, ('%' + searchword + '%', '%' + searchword + '%'))
            notes = cursor.fetchall()
        elif order == "古い順":
            sql = "SELECT * FROM notes WHERE title LIKE %s OR content LIKE %s ORDER BY update_time ASC"
            cursor.execute(sql, ('%' + searchword + '%', '%' + searchword + '%'))
            notes = cursor.fetchall()
    else:
        if order == "新しい順":
            sql = "SELECT * FROM notes ORDER BY update_time DESC"
            cursor.execute(sql)
            notes = cursor.fetchall()
        elif order == "古い順":
            sql = "SELECT * FROM notes ORDER BY update_time ASC"
            cursor.execute(sql)
            notes = cursor.fetchall()
    
    cursor.close()
    connection.close()
    return render_template("index.html", searchword=searchword, orders=orders, notes=notes, len=len(notes),order=order)

@app.route("/note")
def hello_world():
    return render_template("note.html")

@app.route("/delete", methods=["POST"])
def delete_note():
    note_id = int(request.form.get("id"))
    connection = getConnection()
    cursor = connection.cursor()
    sql = "DELETE FROM notes WHERE num = %s"
    cursor.execute(sql, (note_id,))
    global notes
    notes = cursor.fetchall()
    cursor.close()
    connection.close()
    return '', 204  # fetch用なので空レスポンス

if __name__ == '__main__':
    app.run(debug=True)