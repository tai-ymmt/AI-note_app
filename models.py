from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    num = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(16), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    ai_level_flag = db.Column(db.Integer, default=1, nullable=False)    #0:初級 1:中級（デフォルト）2:上級
    ai_answer_flag = db.Column(db.Integer, default=0, nullable=False)   #0:シンプル（デフォルト）1:詳細 2:箇条書き
    mode_flag = db.Column(db.Integer, default=1, nullable=False)        #0:ダークモード 1:ライトモード（デフォルト）

    def get_id(self):
        return self.num

    def __repr__(self):
        return f'<User {self.user_id}>'


class Note(db.Model):
    __tablename__ = 'notes'

    num = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_num = db.Column(db.Integer,nullable=False)
    title = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, default=1, nullable=True)
    update_time = db.Column(db.DateTime,default=datetime.utcnow)

    def __repr__(self):
        return self.title