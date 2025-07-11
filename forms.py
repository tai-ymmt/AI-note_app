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
        Regexp(r'^[a-zA-Z0-9]+$', message='使用できない文字が含まれています')

    ],
    render_kw={"placeholder": "半角英数字で入力してください"}
    )

    password = PasswordField('パスワード', validators=[
        DataRequired(),
        Length(min=8, max=16, message='パスワードは8文字以上16文字以下で入力してください'),
        Regexp(
            r'^[a-zA-z0-9]+$',
            message='使用できない文字が含まれています'
        )
    ],
    render_kw={"placeholder": "半角英数字で8~16文字で入力してください"}
    )

    confirm = PasswordField('パスワード（確認）', validators=[
        DataRequired(),
        Length(min=8, max=16, message='パスワードは8文字以上16文字以下で入力してください'),
        EqualTo('password', message='パスワードが一致しません')
    ],
    render_kw={"placeholder": "再度同じパスワードを入力してください"}
    )

    submit = SubmitField('登録')

#登録されているかチェック
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('既に使用されているユーザーIDです')
        
#パスワードハッシュ化処理
    def get_hashed_password(self):
        return generate_password_hash(self.password.data)

#ログインフォーム
class LoginForm(FlaskForm):
    user_id = StringField('ユーザーID', validators=[
        DataRequired(),
        Length(max=20)
    ],
    render_kw={"placeholder": "半角英数字で20文字以内で入力してください"}
    )

    password = PasswordField('パスワード', validators=[
        DataRequired(),
        Length(min=8, max=16, message='パスワードは8文字以上で入力してください')
    ],
    render_kw={"placeholder": "半角英数字で8文字以上で入力してください"}
    )

    submit = SubmitField('ログイン')

#パスワードハッシュ化処理
    def get_hashed_password(self):
        return generate_password_hash(self.password.data)
    

#パスワード変更フォーム
class ChangePasswordForm(FlaskForm):
    now_password = PasswordField('現在のパスワード', validators=[
        DataRequired(),
        Length(min=8,max=16),
    Regexp(
            r'^[a-zA-Z0-9]+$',
            message='使用できない文字が含まれています'
    )],
    render_kw={"placeholder": "現在のパスワードを入力してください"}
    )

    changed_password = PasswordField('新しいパスワード', validators=[
        DataRequired(),
        Length(min=8, max=16, message='パスワードは8文字以上16文字以下で入力してください。'),
        Regexp(
            r'^[a-zA-Z0-9]+$',
            message='使用できない文字が含まれています'
            )
    ],
    render_kw={"placeholder": "新しいパスワードを入力してください"}
    )

    changed_confirm = PasswordField('新しいパスワード（確認）', validators=[
        DataRequired(),
        Length(min=8, max=16),
        EqualTo('changed_password', message='パスワードが一致しません。')

    ],
    render_kw={"placeholder": "再度同じパスワードを入力してください"}
    )

    submit = SubmitField('変更')

#パスワードハッシュ化処理
    def get_hashed_password(self):
        return generate_password_hash(self.password.data)
