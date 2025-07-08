from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
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


@app.route('/custom')
def settings_page():
    return render_template('custom.html')

@app.route('/custom', methods=['GET', 'POST'])
@login_required
def save_setting():
    if request.method == 'POST':
        data = request.get_json()
        try:
            current_user.mode_flag = int(data.get('mode_flag', current_user.mode_flag))
            current_user.ai_answer_flag = int(data.get('ai_answer_flag', current_user.ai_answer_flag))
            current_user.ai_level_flag = int(data.get('ai_level_flag', current_user.ai_level_flag))
            db.session.commit()
            return jsonify(success=True)
        except Exception as e:
            print("保存エラー:", e)
            return jsonify(success=False), 500
    else:
        return render_template('custom.html')

if __name__ == '__main__':
    app.run(debug=True)