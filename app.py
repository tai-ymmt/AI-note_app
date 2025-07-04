from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, User

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    return render_template('index.html', name=current_user.user_id)

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


orders = ["新しい順", "古い順"]
notes = [
    {"id":1, "title": "ノート1",  "date": "2000-01-01", "content": "こんにちは"},
    {"id":2, "title": "ノート2",  "date": "2000-01-02", "content": "こんばんは"},
    {"id":3, "title": "ノート3",  "date": "2000-01-03", "content": "おはようございます"},
]
print(len(notes))

@app.route("/", methods=["GET", "POST"])
def index():
    searchword = ""
    order = "新しい順"
    filtered_notes = notes.copy()
    if request.method == "POST":
        searchword = request.form.get("searchword")
        order = request.form.get('order')
    
    if searchword:
        filtered_notes = [note for note in notes if searchword in note['title'] or searchword in note['content']]
    else:
        filtered_notes = notes.copy()
    
    if order == "新しい順":
        filtered_notes.sort(key=lambda x: x['date'], reverse=True)
    elif order == "古い順":
        filtered_notes.sort(key=lambda x: x['date'], reverse=False)
    return render_template("index.html", searchword=searchword, orders=orders, notes=filtered_notes, len=len(notes),order=order)

@app.route("/note")
def hello_world():
    return render_template("note.html")

@app.route("/delete", methods=["POST"])
def delete_note():
    note_id = int(request.form.get("id"))
    global notes
    notes = [note for note in notes if note["id"] != note_id]
    return '', 204  # fetch用なので空レスポンス

if __name__ == '__main__':
    app.run(debug=True)