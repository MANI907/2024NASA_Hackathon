from flask import Flask, render_template, request, redirect, session, jsonify, url_for, flash
from pymongo import MongoClient
import numpy as np
import subprocess
from tensorflow.keras.models import load_model
import subprocess  # Pygame 게임 실행을 위한 모듈

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 세션 관리를 위한 비밀키

# MongoDB 클라이언트 설정
client = MongoClient('mongodb://localhost:27017/')
db = client['GAMEDB']  # 데이터베이스 이름을 설정하세요.
users_collection = db['users']  # 사용자 데이터를 저장하는 컬렉션

# 모델 불러오기
model = load_model('./models/my_model.keras')

# 게임 상태와 점수를 저장할 전역 변수
game_status = "Coin Mode 실행 중!"
last_score = 0

# 메인 페이지 - 로그인 페이지로 리다이렉트
@app.route('/')
def home():
    return redirect(url_for('login'))

# 로그인 페이지
@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

# 로그인 처리
@app.route('/login', methods=['POST'])
def login_user():
    username = request.form['username']
    password = request.form['password']
    time_in_space = int(request.form['time'])  # 입력된 시간 값

    # 사용자가 존재하는지 확인
    user = users_collection.find_one({"user_id": username})


    if user:
        # 비밀번호 확인 (단순 텍스트 매칭, 실제로는 해시된 비밀번호 사용 권장)
        if user['password'] == password:
            # 사용자 데이터의 time_in_space 값을 업데이트
            users_collection.update_one(
                {"user_id": username},  # 업데이트할 조건
                {"$set": {"time_in_space": time_in_space}}  # time_in_space 값을 업데이트
            )
            # 사용자 정보를 세션에 저장
            session['user'] = {
                'user_id': user['user_id'],
                'time_in_space': time_in_space,  # 업데이트된 값
                'gender': user['gender'],
                'gravity': user['gravity']
            }
            flash('로그인 성공! 우주 체류기간 업데이트 완료! 예측을 수행합니다.')
            return redirect(url_for('mode_select'))  # 로그인 성공 후 대시보드로 이동 (예시)
        else:
            flash('비밀번호가 올바르지 않습니다.')
    else:
        flash('사용자를 찾을 수 없습니다.')

    return redirect(url_for('login'))  # 로그인 실패 시 다시 로그인 페이지로

    # 로그인 성공 여부 확인 (단순화된 로그인 로직)
    if username == 'user' and password == 'pass':
        session['username'] = username
        session['time_in_space'] = int(request.form['time'])  # 세션에 시간 정보 저장

        # 로그인 성공 시 게임 모드 선택 화면으로 리다이렉트
        return redirect(url_for('mode_select'))
    else:
        return "로그인 실패!", 401

# 예측 수행
@app.route('/perform_prediction')
def perform_prediction():
    user_data = session.get('user')

    if user_data:
        time_in_space = user_data['time_in_space']
        gender = user_data['gender']
        gravity = user_data['gravity']

        # 입력 데이터를 기반으로 예측에 필요한 데이터 전처리
        X_space_exp_input = np.exp(-0.00062 * np.array([time_in_space]))
        input_data = np.column_stack((X_space_exp_input, [gender], [gravity]))

        # 모델을 사용해 예측 수행
        predictions = model.predict(input_data)
        predicted_mip = predictions[0][0]

        # 예측 결과를 세션에 저장
        session['predicted_mip'] = predicted_mip

        flash(f'Predicted MIP: {predicted_mip}')
        return redirect(url_for('mode_select'))

    return "로그인 필요", 401
# 게임 모드 선택 페이지
@app.route('/mode_select', methods=['GET'])
def mode_select():
    predicted_mip = session.get('predicted_mip', '예측 값 없음')
    return render_template('mode_select.html')

# 게임 모드 실행
@app.route('/run_modeA', methods=['POST'])
def run_modeA():
    # 세션에서 예측값 가져오기
    predicted_mip = session.get('predicted_mip')

    if predicted_mip:
        # 'obstacleMode.py' 실행 및 세션 값 전달
        flash(f"Starting OBSTACLE MODE with predicted MIP: {predicted_mip}")

        # subprocess로 obstacleMode.py 실행 (예측값을 전달 가능)
        subprocess.Popen(['python', 'obstacleMode.py', str(predicted_mip)])

        return redirect(url_for('mode_select'))
    else:
        flash('예측값이 필요합니다. 로그인 후 다시 시도해주세요.')
        return redirect(url_for('mode_select'))

@app.route('/run_modeB', methods=['POST'])
def run_modeB():
    subprocess.Popen(["python", "coinMode2.py"])
    return render_template('coinMode.html', status=game_status, score=last_score)


# 점수 저장하는 엔드포인트
@app.route('/save_score', methods=['POST'])
def save_score():
    score = request.json['score']  # JSON 데이터로부터 점수 받기
    session['score'] = score  # 세션에 점수 저장
    return jsonify({"message": "Score saved successfully!"})

# Coin Mode 종료 후 결과 페이지
@app.route('/coin_mode_end')
def coin_mode_end():
    score = session.get('score', 0)  # 세션에서 점수 가져오기
    return render_template('coinMode.html', message=f"Coin Mode 종료! 점수: {score}")

# 점수를 업데이트하는 API 엔드포인트
@app.route('/update_score/<int:score>', methods=['POST'])
def update_score(score):
    global game_status, last_score
    game_status = "Coin Mode 종료!"
    last_score = score
    return jsonify({"message": "Score updated successfully!"})

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    time = np.exp(-0.00062 * np.array([data['time']]))
    gender = np.array([data['gender']])
    gravity = np.array([data['gravity']])

    input_data = np.column_stack((time, gender, gravity))
    prediction = model.predict(input_data)

    return jsonify({'predicted_mip': prediction[0][0]})

# 404 오류 처리 (디버깅용)
@app.errorhandler(404)
def page_not_found(e):
    return f"404 Not Found: {request.url}", 404

if __name__ == '__main__':
    app.run(debug=True)
