from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, User, Note
from datetime import datetime

# # AI用
# from google import genai
# GENAI_API_KEY = "AIzaSyCjjC-YoxhZIzNlCfznMeKQg138BptwDHU"
# client = genai.Client(api_key=GENAI_API_KEY)


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


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    notes = Note.query.all()

    searchword = ""
    order = "新しい順"

    if request.method == "POST":
        searchword = request.form.get("searchword")
        order = request.form.get('order')
    
    if searchword:
        if order == "新しい順":
            notes = Note.query.filter((Note.user_num == current_user.num) & ((Note.title.like(f'%{searchword}%')) | (Note.content.like(f'%{searchword}%')))).order_by(Note.update_time.desc()).all()

        elif order == "古い順":
            notes = Note.query.filter((Note.user_num == current_user.num) & ((Note.title.like(f'%{searchword}%')) | (Note.content.like(f'%{searchword}%')))).order_by(Note.update_time.asc()).all()
    else:
        if order == "新しい順":
            notes = Note.query.filter(Note.user_num == current_user.num).order_by(Note.update_time.desc()).all()
        elif order == "古い順":
            notes = Note.query.filter(Note.user_num == current_user.num).order_by(Note.update_time.asc()).all()
    return render_template("index.html", searchword=searchword, orders=orders, notes=notes, len=len(notes),order=order)

@app.route("/remove", methods=["POST"])
@login_required
def remove_note():
    try:
        note_id = int(request.form.get("id"))
        destroy_note = Note.query.get(note_id)
        if destroy_note is None:
            return {"message": "ノートが見つかりませんでした。"}, 404
        
        db.session.delete(destroy_note)
        db.session.commit()
        
        return {"message": "削除しました"}, 200
    except Exception as e:
        db.session.rollback()
        return {"message": f"削除に失敗しました: {str(e)}"}, 500



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
    note.update_time = datetime.utcnow()
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

@app.route('/newUser', methods=['GET', 'POST'])
def newUser():
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # すでにログイン済みならリダイレクト

    form = NewUserForm()
    
    if form.validate_on_submit():
        # フォームの入力内容を元に新規ユーザー作成
        hashed_password = form.get_hashed_password()  # ハッシュ化されたパスワードを取得

        new_user = User(
            user_id=form.user_id.data,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('ユーザー登録が完了しました。ログインしてください。')
        return redirect(url_for('login'))  # login ページにリダイレクト
    
    return render_template('new_user.html', form=form)

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
    ai_level_flag = int(data.get('ai_level_flag', current_user.ai_level_flag))
    ai_answer_flag = int(data.get('ai_answer_flag', current_user.ai_answer_flag))

    if not keyword:
        return jsonify({'result': 'キーワードを入力してください'}), 400

    # プロンプト生成（条件分岐で内容を変える）
    # 出力形式（ai_answer_flag）: 0=シンプル, 1=詳細, 2=箇条書き
    # 難易度（ai_level_flag）: 0=初学者, 1=普通, 2=専門的

    format_text = {
        0: "できるだけ簡潔に（要点だけをまとめて200文字程度で）",
        1: "詳細に、できるだけ具体的に（400文字程度で）",
        2: "要点をまとめて箇条書きで4行程度で"
    }[ai_answer_flag]

    level_text = {
        0: "初心者向けに",
        1: "一般的なレベルで",
        2: "専門家向けに"
    }[ai_level_flag]

    prompt = f"{keyword}について{level_text}、{format_text}、前置きはなくして日本語で解説してください。"

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

@app.route('/settings')
def settings_page():
    return render_template('settings.html')




if __name__ == '__main__':
    app.run(debug=True)