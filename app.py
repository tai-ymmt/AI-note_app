from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from forms import LoginForm, NewUserForm ,ChangePasswordForm
from models import db, User, Note

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

#login_manegerの設定（未ログイン時のアドレスはloginページへ）
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(num):
    return User.query.get(int(num))

@login_manager.unauthorized_handler
def unauthorized():
    flash('ログインが必要です。先にログインしてください。', 'danger')  # カスタムメッセージ
    return redirect(url_for('login'))


#一覧ページへ
@app.route('/')
@login_required
def index():
    return render_template('index.html', user_id=current_user.user_id)

#ログインページへ
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # すでにログイン済みならリダイレクト

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_id=form.user_id.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('ユーザーIDかパスワードが正しくありません。','danger')
            return redirect(url_for('login'))

    return render_template('login.html', form=form)

#新規登録
@app.route('/newUser', methods=['GET', 'POST'])
def newUser():
    form = NewUserForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # すでにログイン済みならリダイレクト
    
    if User.query.filter_by(user_id=form.user_id.data).first():
        flash('そのユーザーIDは使用されています','danger')
        return render_template('new_user.html', form=form)
    
    if form.validate_on_submit():
        # フォームの入力内容を元に新規ユーザー作成
        hashed_password = form.get_hashed_password()  # ハッシュ化されたパスワードを取得

        new_user = User(
            user_id=form.user_id.data,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('ユーザー登録が完了しました。ログインしてください。','danger')
        return redirect(url_for('login'))  # login ページにリダイレクト
    
    return render_template('new_user.html', form=form)

#ログアウト
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('ログアウトしました。','success')

    return redirect(url_for('login'))

#パスワード変更
@app.route('/changePassword', methods=['GET', 'POST'])
@login_required
def changePassword():
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        # 現在のパスワードチェック
        if not check_password_hash(current_user.password, form.now_password.data):
            flash('現在のパスワードが正しくありません','danger')
            return render_template('change_pass.html', form=form)
        
        #現在と一致している場合エラー
        if check_password_hash(current_user.password, form.changed_password.data):
            flash('新しいパスワードが現在のパスワードと同じです','danger')
            return render_template('change_pass.html', form=form)
        
        current_user.password = generate_password_hash(form.changed_password.data)
        db.session.commit()
        #遷移前にログアウト
        logout_user()
        flash('パスワード変更しました。ログインしてください','success')
        return redirect(url_for('login'))
    
    return render_template('change_pass.html',form=form)



if __name__ == '__main__':
    app.run(debug=True)
