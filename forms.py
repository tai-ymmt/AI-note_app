from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import (
    DataRequired, EqualTo, Length, Regexp, ValidationError
)
from werkzeug.security import generate_password_hash
from models import User,  Note  # SQLAlchemyのUserモデルをインポート

#新規登録
class NewUserForm(FlaskForm):
    user_id = StringField('ユーザーID', validators=[
        DataRequired(),
        Length(max=20),
        Regexp(r'^[a-zA-Z0-9]+$', message='ユーザー名は半角英数字のみ使用できます。')

    ],
    render_kw={"placeholder": "半角英数字で入力をお願いします"}
    )

    password = PasswordField('パスワード', validators=[
        DataRequired(),
        Length(min=8, max=16, message='パスワードは8文字以上16文字以下で入力してください。'),
        Regexp(
            r'^[a-zA-z0-9]+$',
            message='パスワードは半角英数字のみで作成してください'
        )
    ],
    render_kw={"placeholder": "半角英数字で8~16文字で入力をお願いします"}
    )

    confirm = PasswordField('パスワード（確認）', validators=[
        DataRequired(),
        Length(min=8, max=16, message='パスワードは8文字以上16文字以下で入力してください。'),
        EqualTo('password', message='パスワードが一致しません。')
    ],
    render_kw={"placeholder": "パスワード欄と同じものを入力してください"}
    )

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
    ],
    render_kw={"placeholder": "半角英数字で20文字以内"}
    )

    password = PasswordField('パスワード', validators=[
        DataRequired(),
        Length(min=8, max=16, message='パスワードは8文字以上')
    ],
    render_kw={"placeholder": "半角英数字で8文字以上"}
    )

    submit = SubmitField('ログイン')

#パスワードハッシュ化処理
    def get_hashed_password(self):
        return generate_password_hash(self.password.data)
    

#パスワード変更フォーム
class ChangePasswordForm(FlaskForm):
    now_password = PasswordField('現在のパスワード', validators=[
        DataRequired(),
        Length(min=8,max=16)
    ],
    render_kw={"placeholder": "現在のパスワードを入力してください"}
    )

    changed_password = PasswordField('新しいパスワード', validators=[
        DataRequired(),
        Length(min=8, max=16, message='パスワードは8文字以上16文字以下で入力してください。'),
        Regexp(
            r'^[a-zA-Z0-9]+$',
            message='パスワードは半角英数字のみで作成してください'
            )
    ],
    render_kw={"placeholder": "半角英数字で現在とは異なるパスワードを入力"}
    )

    changed_confirm = PasswordField('新しいパスワード（確認）', validators=[
        DataRequired(),
        Length(min=8, max=16),
        EqualTo('changed_password', message='パスワードが一致しません。')

    ],
    render_kw={"placeholder": "新しいパスワード欄と同じものを入力してください"}
    )

    submit = SubmitField('変更')

#パスワードハッシュ化処理
    def get_hashed_password(self):
        return generate_password_hash(self.password.data)
