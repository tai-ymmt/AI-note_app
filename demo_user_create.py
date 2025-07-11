from main import app
from models import db, User
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
