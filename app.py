import mysql.connector
import os
#python 環境變數套件
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, jsonify;

#呼叫套件 預設載入.env
load_dotenv()
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    #呼叫環境變數 SQL_PD為自訂
    password=os.getenv("SQL_PD"),
    database="website",
    charset = "utf8"
)
mycursor = mydb.cursor()

#首頁
@app.route('/')
def index():
    return render_template('index.html')

#註冊
@app.route('/signup', methods=["POST"])
def signup():
    #取得使用者註冊資料
    username = request.form.get("username")
    name = request.form.get("name")
    password = request.form.get("password")
    #input不得為空
    if not username or not name or not password:
        return redirect(url_for("error", message="資料不得為空"))

    #執行mysql指令碼 檢查帳號是否被註冊過 
    sqlcmd = f"SELECT 1 FROM user WHERE username ='{username}' limit 1"
    mycursor.execute(sqlcmd)
    myResult = mycursor.fetchone()

    #帳號已被註冊過 進入error頁面
    if myResult:
        return redirect(url_for("error", message="帳號已經被註冊"))
    #註冊流程
    else:
        addsqlcmd = f"INSERT INTO user(name, username, password) VALUES('{name}', '{username}', '{password}')"
        mycursor.execute(addsqlcmd)
        mydb.commit()
        return redirect(url_for("index"))

#登入
@app.route('/signin', methods=["POST"])
def signin():
    #取得登入資料
    signinUsername = request.form.get("signinUsername")
    signinPassword = request.form.get("signinPassword")

     #input不得為空
    if not signinUsername or not signinPassword:
        return redirect(url_for("error", message="資料不得為空"))
    
    #SQL指令 檢查登入帳密是否正確
    mysqlcmd = f"SELECT 1 FROM user WHERE username = '{signinUsername}' and password = '{signinPassword}'" 
    mycursor.execute(mysqlcmd)
    myResult = mycursor.fetchone()
    
    #登入成功進入member頁面 失敗則error
    if myResult:
        session['username'] = signinUsername
        return redirect(url_for("member"))
    else:
        return redirect(url_for("error", message="帳號或密碼輸入錯誤"))

#登出
@app.route('/signout')
def signout():
    session["username"] = False
    return redirect(url_for("index"))

#會員頁
@app.route('/member')
def member():
    #取得session中的登入資訊
    getSession = session.get("username")

    #利用session資料 取得使用者的name 如果session沒資料代表未登入 導向到首頁
    if getSession:
        mysqlcmd = f"SELECT name from user WHERE username = '{getSession}'"
        mycursor.execute(mysqlcmd)
        myResult = mycursor.fetchone()

        #用for來去除mysql指令產生多餘的符號 ('',)
        for name in myResult:
            #render_template參數不會產生在網址上
            return render_template("member.html", name=name)
    else:
        return redirect(url_for("index"))

#錯誤頁面
@app.route('/error/')
def error():
    errorMessage = request.args.get("message")
    return render_template("error.html", message=errorMessage)


#第七周作業
#api
@app.route('/api/users')
def userAPI():
    #取得session中的登入資訊
    getSession = session.get("username")
    
    
    if getSession:
        #取得query string
        username = request.args.get('username')
        mysqlcmd = f"SELECT * FROM user WHERE username = '{username}'"
        
        mycursor.execute(mysqlcmd)
        myResult = mycursor.fetchone()

        if myResult:
            return jsonify({
                "data":{
                    "id":myResult[0],
                    "name":myResult[1],
                    "username":myResult[2]
                }   
            })
        else:
            return jsonify({
                "data":"null"
            })
    #未登入過redirect回首頁
    else:
        return redirect(url_for("index"))

app.run(port=3000)




