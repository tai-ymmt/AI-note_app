#実行にあたっての環境構築について
１．requirements.txtの内容インストール
    下記のコードを実行
        pip install -r requirements.txt

２．SQLユーザーの作成
    下記ユーザーの作成と権限の付与
        ユーザー名:note_User
        パスワード:NOTE-uSER
        全権限の付与

    下記コード実行
        source create.sql (mysql -u （ユーザー名）-p　実施後に実行)
        python demo_user_create.py


#サーバーの起動について
    下記のコードを実行
        set FLASK_APP=app.py
        set FLASK_ENV=development
        flask run

    下記アドレスを開く
        http://localhost:5000/login
