import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np

# 1. 데이터 준비

# 경로 설정 (데이터 파일 경로에 맞게 수정 필요)
gravity_data_path = r'C:\Users\USER\Downloads\male_gravity_data.csv'
female_gravity_data_path = r'C:\Users\USER\Downloads\female_gravity_data.csv'
male_zero_gravity_data_path = r'C:\Users\USER\Downloads\male_zero_gravity_data.csv'
female_zero_gravity_data_path = r'C:\Users\USER\Downloads\female_zero_gravity_data.csv'

# CSV 파일 불러오기
male_gravity_data = pd.read_csv(gravity_data_path)
female_gravity_data = pd.read_csv(female_gravity_data_path)
male_zero_gravity_data = pd.read_csv(male_zero_gravity_data_path)
female_zero_gravity_data = pd.read_csv(female_zero_gravity_data_path)

# 중력 상태 열 추가: 지구 중력은 1, 무중력은 0으로 설정
male_gravity_data['Gravity'] = 1  # 중력 상태
female_gravity_data['Gravity'] = 1  # 중력 상태
male_zero_gravity_data['Gravity'] = 0  # 무중력 상태
female_zero_gravity_data['Gravity'] = 0  # 무중력 상태

# 성별 열 추가: 남성은 1, 여성은 0
male_gravity_data['Gender'] = 1  # 남성
female_gravity_data['Gender'] = 0  # 여성
male_zero_gravity_data['Gender'] = 1  # 남성
female_zero_gravity_data['Gender'] = 0  # 여성

# 모델 구축 함수 (드롭아웃 비율과 학습률 조정)
def build_model():
    model = models.Sequential()
    model.add(layers.Dense(128, activation='relu', input_shape=(3,)))  # 입력층 (시간, 성별, 중력 상태)
    model.add(layers.Dropout(0.2))  # 드롭아웃 비율 줄임
    model.add(layers.Dense(64, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.001)))  # L2 정규화 줄임
    model.add(layers.Dense(32, activation='relu'))
    model.add(layers.Dense(1, activation='linear'))  # 회귀 문제이므로 linear 사용
    return model

# 학습률 스케줄러
lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
    initial_learning_rate=0.0005,  # 학습률을 줄여서 학습
    decay_steps=10000, decay_rate=0.96, staircase=True
)

# Adam 옵티마이저에 학습률 스케줄러 적용
optimizer = tf.keras.optimizers.Adam(learning_rate=lr_schedule)

# 모델 컴파일 및 훈련 프로세스는 동일하게 유지


# 모든 데이터를 병합
combined_data = pd.concat([male_gravity_data, female_gravity_data, male_zero_gravity_data, female_zero_gravity_data], ignore_index=True)

# 2. 입력 데이터 준비

# 열 이름 자동 확인 및 처리
# 'Time_in_Space'가 없으면 기본 값을 180일로 설정
if 'Time_in_Space' in combined_data.columns:
    time_values = combined_data['Time_in_Space']
else:
    # 유사한 열 이름이 없을 때 기본 값 설정
    time_values = np.full(len(combined_data), 180)  # 기본 값으로 180일 설정 (모든 행)

# 성별과 중력 상태 데이터
gender_values = combined_data['Gender']
gravity_values = combined_data['Gravity']

# 시간 데이터를 지수적으로 감소시킨 값
X_space_exp_input = np.exp(-0.00062 * time_values)

# 입력 데이터 병합 (시간 + 성별 + 중력 상태)
X_combined = np.column_stack((X_space_exp_input, gender_values, gravity_values))

# 출력 데이터 (MIP 값)
y_mip = combined_data['MIP']

# 3. 모델 구성

# 모델 구축 함수
def build_model():
    model = models.Sequential()
    model.add(layers.Dense(128, activation='relu', input_shape=(3,)))  # 입력층 (시간, 성별, 중력 상태)
    model.add(layers.Dropout(0.3))  # 드롭아웃 비율 증가
    model.add(layers.Dense(64, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.01)))  # L2 정규화 추가
    model.add(layers.Dense(32, activation='relu'))
    model.add(layers.Dense(1, activation='linear'))  # 회귀 문제이므로 linear 사용
    return model

# 학습률 스케줄러
lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
    initial_learning_rate=0.001, decay_steps=10000, decay_rate=0.96, staircase=True
)

# Adam 옵티마이저에 학습률 스케줄러 적용
optimizer = tf.keras.optimizers.Adam(learning_rate=lr_schedule)

# 모델 컴파일
model = build_model()
model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])

# 조기 종료 콜백 추가
early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

# 4. 데이터 분할 및 훈련

# 데이터 분할 (80% 훈련, 20% 검증)
X_train, X_val, y_train, y_val = train_test_split(X_combined, y_mip, test_size=0.2, random_state=42)

# 모델 훈련
history = model.fit(X_train, y_train, epochs=100, batch_size=16, validation_data=(X_val, y_val), callbacks=[early_stopping], verbose=1)

# 5. 모델 평가

mse, mae = model.evaluate(X_val, y_val)
print(f"Mean Squared Error: {mse}, Mean Absolute Error: {mae}")

# 6. 예측 (새로운 데이터 입력 예시)

# 새로운 시간, 성별, 중력 상태 데이터
new_time_data = np.array([50, 100, 180])  # 시간 값
new_gender_data = np.array([1, 0, 1])  # 남성: 1, 여성: 0
new_gravity_data = np.array([1, 0, 0])  # 중력: 1, 무중력: 0

# 로그 변환 및 지수 함수 적용
new_time_exp = np.exp(-0.00062 * new_time_data)

# 새로운 입력 데이터 병합 (시간, 성별, 중력 상태)
new_input_data = np.column_stack((new_time_exp, new_gender_data, new_gravity_data))

# 예측
predictions = model.predict(new_input_data)
print("Predicted MIP values:", predictions)

# 딥러닝 모델 저장
model.save('mip_prediction_model.h5')

from tensorflow.keras.models import load_model

# 모델 불러오기
model = load_model('mip_prediction_model.h5')

# 새로운 데이터를 기반으로 예측
predictions = model.predict(new_input_data)

import pandas as pd

# CSV 파일 불러오기
player_data = pd.read_csv('player_data.csv')

# 모델에 입력할 데이터 생성
time_values = player_data['Time_in_Space']
gender_values = player_data['Gender']
gravity_values = player_data['Gravity']

# 예측에 필요한 데이터 전처리
X_space_exp_input = np.exp(-0.00062 * time_values)
input_data = np.column_stack((X_space_exp_input, gender_values, gravity_values))




from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
import numpy as np

# Flask 앱 생성
app = Flask(__name__)

# 모델 불러오기
model = load_model('mip_prediction_model.h5')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    time = np.exp(-0.00062 * np.array([data['time']]))
    gender = np.array([data['gender']])
    gravity = np.array([data['gravity']])

    input_data = np.column_stack((time, gender, gravity))
    prediction = model.predict(input_data)

    return jsonify({'predicted_mip': prediction[0][0]})

# 서버 실행
if __name__ == '__main__':
    app.run(debug=True)
