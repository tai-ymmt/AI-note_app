from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import (
    DataRequired, EqualTo, Length, Regexp, ValidationError
)
from werkzeug.security import generate_password_hash
from models import User  # SQLAlchemyのUserモデルをインポート
from models import Note  # SQLAlchemyのNoteモデルをインポート

#新規登録
class NewUserForm(FlaskForm):
    user_id = StringField('ユーザーID', validators=[
        DataRequired(),
        Length(max=20),
        Regexp(r'^[a-zA-Z0-9]+$', message='ユーザー名は半角英数字のみ使用できます。')
    ])

    password = PasswordField('パスワード', validators=[
        DataRequired(),
        Length(min=8, max=64, message='パスワードは8文字以上64文字以下で入力してください。'),
        Regexp(
            r'^(?=.*[a-zA-Z])(?=.*[0-9])[a-zA-Z0-9]+$',
            message='パスワードは半角英数字のみで、英字と数字の両方を含めてください。'
        )
    ])

    confirm = PasswordField('パスワード（確認）', validators=[
        DataRequired(),
        EqualTo('password', message='パスワードが一致しません。')
    ])

    submit = SubmitField('登録')

#登録されているかチェック
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('このユーザー名はすでに使用されています。')
        
#パスワードハッシュ化処理
    def get_hashed_password(self):
        return generate_password_hash(self.password.data)

#ログインフォーム
class LoginForm(FlaskForm):
    user_id = StringField('ユーザーID', validators=[
        DataRequired(),
        Length(max=20)
    ])

    password = PasswordField('パスワード', validators=[
        DataRequired(),
        Length(min=8, max=16)
    ])

    submit = SubmitField('ログイン')

#パスワードハッシュ化処理
    def get_hashed_password(self):
        return generate_password_hash(self.password.data)
