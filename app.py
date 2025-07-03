from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from forms import LoginForm, NewUserForm
from models import db, User, Note

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

#login_manegerの設定（未ログイン時のアドレスはloginページへ）
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#一覧ページへ
@app.route('/')
@login_required
def index():
    return render_template('index.html', name=current_user.user_id)

#ログインページへ
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # すでにログイン済みならリダイレクト

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('ログインしました。')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('ユーザー名かパスワードが正しくありません。')

    return render_template('login.html', form=form)

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

#ログアウト
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
