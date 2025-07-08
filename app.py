from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, User, Note #本田　この末尾に「Note」を追加するのは忘れないで
from datetime import datetime

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
# これより上は他の人のに合わせて
# ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓本田ノート一覧画面　オリジナル部分↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓

# 並び替えプルダウンの中身
orders = ["新しい順", "古い順"]

# ノート一覧画面
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

# ノート一覧画面でのノート削除
@app.route("/remove", methods=["POST"])
@login_required
def remove_note():
    try:
        note_id = int(request.form.get("id"))
        destroy_note = Note.query.get(note_id)
        if destroy_note is None:
            return {"message": "ノートが見つかりませんでした"}, 404
        
        db.session.delete(destroy_note)
        db.session.commit()
        
        return {"message": "削除しました"}, 200
    except Exception as e:
        db.session.rollback()
        return {"message": f"削除に失敗しました: {str(e)}"}, 500

#ノート一覧画面でのノート新規作成（これは山本さんのやつに合わせた方がいい）
@app.route('/note/create', methods=['POST'])
@login_required
def create_note():
    note = Note(title="新しいノート", content="", user_num=current_user.num)
    db.session.add(note)
    db.session.commit()
    return jsonify({'note_id': note.num})

#ノート一覧画面で各ノートタイトルを押したとき、編集画面へ遷移
@app.route('/note/<int:note_id>')
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_num != current_user.num:
        return "権限がありません", 403
    return render_template('note.html', note=note)

# ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑本田ノート一覧画面　オリジナル部分↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
# これより下は他の人のに合わせて

if __name__ == '__main__':
    app.run(debug=True)