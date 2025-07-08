from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, logout_user
from werkzeug.security import check_password_hash
from config import Config
from models import db, User, Note
from forms import LoginForm, NewUserForm
from datetime import datetime

# Google Gemini API 用の設定
from google import genai
GENAI_API_KEY = "AIzaSyCjjC-YoxhZIzNlCfznMeKQg138BptwDHU"
client = genai.Client(api_key=GENAI_API_KEY)

# Flaskアプリ本体・DB設定
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Flask-Login ログインマネージャー設定
login_manager = LoginManager()
login_manager.login_view = 'login'  # 未ログイン時はloginページに飛ぶ
login_manager.init_app(app)

# Flask-Loginのユーザー読み出し
@login_manager.user_loader
def load_user(num):
    return User.query.get(int(num))

# 並び順の選択肢
orders = ["新しい順", "古い順"]

# ----------- ノート一覧・検索・並び順 -----------
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """ノート一覧画面。検索・並び替え・件数も返す"""
    searchword = ""
    order = "新しい順"
    notes = Note.query.all()

    if request.method == "POST":
        searchword = request.form.get("searchword")
        order = request.form.get('order')
    
    # 検索ありの場合、タイトル・本文部分一致で検索
    if searchword:
        query = Note.query.filter(
            (Note.user_num == current_user.num) &
            ((Note.title.like(f'%{searchword}%')) | (Note.content.like(f'%{searchword}%')))
        )
        notes = query.order_by(
            Note.update_time.desc() if order == "新しい順" else Note.update_time.asc()
        ).all()
    else:
        # 検索なしの場合は全件
        notes = Note.query.filter(
            Note.user_num == current_user.num
        ).order_by(
            Note.update_time.desc() if order == "新しい順" else Note.update_time.asc()
        ).all()
    return render_template("index.html", searchword=searchword, orders=orders, notes=notes, len=len(notes), order=order)

# ----------- ノート新規作成ページ -----------
@app.route('/note/new')
@login_required
def new_note():
    """新規ノート作成画面（空のノートを返す）"""
    default_note = {
        'title': '新しいノート',
        'content': '',
        'num': None  # 新規なので noteId はまだなし
    }
    return render_template('note.html', note=default_note)

# ----------- ノート新規保存・編集保存(共通) -----------
@app.route('/note/save', methods=['POST'])
@login_required
def save_note_new_or_edit():
    """
    新規ノート作成時や、ノート編集後の保存時
    note_idがあれば編集、なければ新規作成
    """
    data = request.json
    note_id = data.get('note_id')
    if note_id:
        # 既存ノートの編集保存
        note = Note.query.get_or_404(note_id)
        if note.user_num != current_user.num:
            return jsonify({'error': '権限がありません'}), 403
    else:
        # 新規作成（DB追加）
        note = Note(user_num=current_user.num)
        db.session.add(note)
    note.title = data.get('title', '')
    note.content = data.get('content', '')
    note.update_time = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': '保存しました', 'note_id': note.num})

# ----------- ノート編集ページ -----------
@app.route('/note/<int:note_id>')
@login_required
def edit_note(note_id):
    """ノート編集画面"""
    note = Note.query.get_or_404(note_id)
    if note.user_num != current_user.num:
        return "権限がありません", 403
    return render_template('note.html', note=note)

# ----------- ノート個別保存（URL付き）-----------
@app.route('/note/<int:note_id>/save', methods=['POST'])
@login_required
def save_note(note_id):
    """既存ノートを個別に保存"""
    note = Note.query.get_or_404(note_id)
    if note.user_num != current_user.num:
        return jsonify({'error': '権限がありません'}), 403
    data = request.json
    note.title = data.get('title', note.title)
    note.content = data.get('content', note.content)
    note.update_time = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': '保存しました'})

# ----------- ノート削除 -----------
@app.route('/note/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_note(note_id):
    """ノートの削除"""
    note = Note.query.get_or_404(note_id)
    if note.user_num != current_user.num:
        return jsonify({'error': '権限がありません'}), 403
    db.session.delete(note)
    db.session.commit()
    return jsonify({'message': '削除しました'})

# ----------- ログインページ -----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    ログイン処理
    - フォーム送信時にID・PW認証（パスワードはハッシュ）
    - 成功ならログイン＆トップへ
    - 失敗ならエラー表示
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # すでにログイン済みならリダイレクト

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_id=form.user_id.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('ユーザーIDかパスワードが正しくありません。', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html', form=form)

# ----------- ログアウト -----------
@app.route('/logout')
@login_required
def logout():
    """ログアウトしてログインページへ"""
    logout_user()
    flash('ログアウトしました。', 'success')
    return redirect(url_for('login'))

# ----------- ユーザー設定ページ -----------
@app.route('/custom')
def settings_page():
    """設定画面（カスタムページ）"""
    return render_template('custom.html')

# ----------- 新規ユーザー登録 -----------
@app.route('/newUser', methods=['GET', 'POST'])
def newUser():
    """
    新規ユーザー登録ページ
    - 同じユーザーIDがあればエラー
    - 登録成功でログイン画面へ
    """
    form = NewUserForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # すでにログイン済みならリダイレクト

    if form.validate_on_submit():
        # 重複チェック
        if User.query.filter_by(user_id=form.user_id.data).first():
            flash('そのユーザーIDは使用されています', 'danger')
            return render_template('new_user.html', form=form)
        # ユーザー作成
        hashed_password = form.get_hashed_password()
        new_user = User(
            user_id=form.user_id.data,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        flash('ユーザー登録が完了しました。ログインしてください。', 'success')
        return redirect(url_for('login'))
    return render_template('new_user.html', form=form)

# ----------- AI要約API（Gemini） -----------
@app.route('/api/ai_search', methods=['POST'])
@login_required
def ai_search():
    """
    AI（Gemini）による要約API
    - keyword, ai_level_flag, ai_answer_flagを受け取り
    - Geminiにプロンプト生成・結果返却
    """
    data = request.json
    keyword = data.get('keyword', '').strip()
    ai_level_flag = int(data.get('ai_level_flag', current_user.ai_level_flag))
    ai_answer_flag = int(data.get('ai_answer_flag', current_user.ai_answer_flag))

    if not keyword:
        return jsonify({'result': 'キーワードを入力してください'}), 400

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

# ----------- アプリ起動 -----------
if __name__ == '__main__':
    app.run(debug=True)
