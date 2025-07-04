from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from config import Config
from models import db, User, Note

# AI用
from google import genai
GENAI_API_KEY = "AIzaSyCjjC-YoxhZIzNlCfznMeKQg138BptwDHU"
client = genai.Client(api_key=GENAI_API_KEY)

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
    notes = Note.query.filter_by(user_num=current_user.num).order_by(Note.update_time.desc()).all()
    #notes = Note.query.filter_by(user_num=current_user.num).order_by(Note.created.desc()).all()
    return render_template('index.html', notes=notes, name=current_user.user_id)

@app.route('/note/create', methods=['POST'])
@login_required
def create_note():
    note = Note(title="新しいノート", content="", user_num=current_user.num)
    db.session.add(note)
    db.session.commit()
    return jsonify({'note_id': note.num})

@app.route('/note/<int:note_id>')
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_num != current_user.num:
        return "権限がありません", 403
    return render_template('note.html', note=note)

@app.route('/note/<int:note_id>/save', methods=['POST'])
@login_required
def save_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_num != current_user.num:
        return jsonify({'error': '権限がありません'}), 403
    data = request.json
    note.title = data.get('title', note.title)
    note.content = data.get('content', note.content)
    db.session.commit()
    return jsonify({'message': '保存しました'})

@app.route('/note/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_num != current_user.num:
        return jsonify({'error': '権限がありません'}), 403
    db.session.delete(note)
    db.session.commit()
    return jsonify({'message': '削除しました'})

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

# ★AI要約API
@app.route('/api/ai_search', methods=['POST'])
@login_required
def ai_search():
    data = request.json
    keyword = data.get('keyword', '').strip()
    if not keyword:
        return jsonify({'result': 'キーワードを入力してください'}), 400

    prompt = f"{keyword}について日本語で200文字程度で解説してください。"
    try:
        client = genai.Client(api_key=GENAI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        summary = response.text.strip()
    except Exception:
        import traceback
        traceback.print_exc()
        summary = "AIによる解説の取得中にエラーが発生しました"
    return jsonify({'result': summary})

# AI設定保存（仮）
@app.route('/api/ai_settings', methods=['POST'])
@login_required
def ai_settings():
    return jsonify({'message': 'AI設定を保存しました'})

if __name__ == '__main__':
    app.run(debug=True)
