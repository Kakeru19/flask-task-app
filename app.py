from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3


app = Flask(__name__)
app.secret_key = "secret_key" 
DB_NAME = "task.db"


#データベース初期化
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    #タスクテーブル作成
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL
        )
    """)
    #ユーザーテーブル作成
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


#メイン画面
@app.route("/", methods=["GET", "POST"])
def index():
    #ログインチェック
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    #タスク追加
    if request.method == "POST":
        title = request.form["title"]
        cur.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
        conn.commit()
        return redirect("/")

    #タスク取得
    cur.execute("SELECT * FROM tasks")
    tasks = cur.fetchall()
    conn.close()

    return render_template("index.html", tasks=tasks)


#タスク削除
@app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect("/")


#ログイン
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["user_id"] = user[0]
            return redirect("/")
        else:
            error = "ログイン失敗"

    return render_template("login.html", error=error)

#ユーザー登録
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(
            password,
            method="pbkdf2:sha256"
        )

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password)
        )
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


#ログアウト
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    print("起動しました")
    init_db()
    app.run(host="0.0.0.0", port=5001, debug=True)


