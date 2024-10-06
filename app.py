from flask import Flask, render_template, redirect, url_for, request, session
from pymongo import MongoClient
import subprocess  # coin.py 실행을 위한 모듈

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB 설정
client = MongoClient('mongodb://localhost:27017/')
db = client['GAMEDB']
users_collection = db['users']

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # 간단한 로그인 인증
    if username == 'user' and password == 'pass':
        session['username'] = username
        return redirect(url_for('mode_select'))
    else:
        return 'Login Failed!'

# 모드 선택 화면 라우트
@app.route('/modeSelect')
def mode_select():
    if 'username' not in session:
        return redirect(url_for('home'))  # 로그인이 안 된 경우 홈으로 이동
    return render_template('mode_select.html')

# mode2 선택 시 coin.py 실행
@app.route('/mode2')
def run_coin_game():
    if 'username' not in session:
        return redirect(url_for('home'))

    # coin.py 게임을 실행 (별도의 창에서 실행)
    subprocess.Popen(["python", "coinMode.py"])  # 여기에 입력!
    return "Coin Game is now running!"  # 웹 페이지에 간단한 메시지 출력

if __name__ == '__main__':
    app.run(debug=True)
