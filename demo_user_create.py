from app import app
from models import db, User, Note
from werkzeug.security import generate_password_hash

with app.app_context():
    if not User.query.filter_by(user_id='demo').first():
        user = User(
        user_id='demo',
        password=generate_password_hash('demopassword')
        )
        db.session.add(user)
        db.session.commit()
        print(" demo ユーザーを作成しました。")
    else:
        print(" demo ユーザーはすでに存在します。")

with app.app_context():
    if not Note.query.filter_by(user_num=1).first():
        note = Note(
        user_num=1,
        title="ノート1",
        content="こんにちは",
        update_time="2025-01-01")
        db.session.add(note)
        db.session.commit()
        print(" demo ノートを作成しました。")
    else:
        print(" demo ノートはすでに存在します。")