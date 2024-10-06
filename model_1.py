import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np

# 1. 데이터 준비

# 경로 설정 (데이터 파일 경로에 맞게 수정 필요)
gravity_data_path = r'C:\Users\sjeon\Downloads\male_gravity_data.csv'
female_gravity_data_path = r'C:\Users\sjeon\Downloads\female_gravity_data.csv'
male_zero_gravity_data_path = r'C:\Users\sjeon\Downloads\male_zero_gravity_data.csv'
female_zero_gravity_data_path = r'C:\Users\sjeon\Downloads\female_zero_gravity_data.csv'

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
model.save('my_model.keras')


from tensorflow.keras.models import load_model

# 모델 불러오기
model = load_model('my_model.keras')
# 모델 컴파일 시 수정
model.compile(optimizer=optimizer, loss='mean_squared_error', metrics=['mean_absolute_error'])


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
model = load_model('my_model.keras')

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



import pygame
import random
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

# Pygame 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("호흡 기반 우주 게임")

# FPS 설정
clock = pygame.time.Clock()

# 색상 설정
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# 캐릭터 이미지 로드
astronaut_img = pygame.image.load('player.jpg')
astronaut_rect = astronaut_img.get_rect()
astronaut_rect.x = 50
astronaut_rect.y = HEIGHT // 2  # 초기 위치는 화면 중앙

# 장애물 리스트
obstacles = []

# 딥러닝 모델 로드
model = load_model(r'C:\Users\sjeon\Downloads\my_model.keras')
# 실시간 호흡 데이터를 받아서 예측하는 함수
def predict_mip_mep(input_data):
    predictions = model.predict(input_data)
    mip = predictions[0][0]  # MIP 예측값
    mep = predictions[0][1]  # MEP 예측값
    return mip, mep

# 가상의 호흡 데이터를 수집하는 함수 (실제 호흡 센서와 연결 시 교체)
def collect_breath_data():
    mip = np.random.uniform(90, 110)  # MIP 데이터 (가상)
    mep = np.random.uniform(80, 100)  # MEP 데이터 (가상)
    return np.array([[mip, mep]])
class Player:
    def __init__(self):
        self.y_position = HEIGHT // 2  # 캐릭터의 초기 위치 (수직 위치)
        self.is_inhaling = False  # 초기 상태는 호기 (내쉬는 상태)

    def update_position(self):
        keys = pygame.key.get_pressed()

        # 위/아래 화살표로 캐릭터 이동
        if keys[pygame.K_UP] and self.is_inhaling:  # 흡기 중일 때 위로 이동
            astronaut_rect.y -= 5
        elif keys[pygame.K_DOWN] and not self.is_inhaling:  # 호기 중일 때 아래로 이동
            astronaut_rect.y += 5

        # 화면 경계 밖으로 나가지 않도록 설정
        astronaut_rect.y = max(0, min(HEIGHT - astronaut_rect.height, astronaut_rect.y))

class Obstacle:
    def __init__(self, direction):
        self.rect = pygame.Rect(WIDTH, random.randint(50, HEIGHT - 50), 50, 50)
        self.direction = direction  # 위로 또는 아래로 이동

    def move(self):
        if self.direction == 'up':
            self.rect.x -= 10  # 오른쪽에서 왼쪽으로 이동
        else:
            self.rect.x -= 10

    def draw(self):
        pygame.draw.rect(SCREEN, RED, self.rect)

# 장애물 생성 함수
def create_obstacle():
    direction = 'up' if random.choice([True, False]) else 'down'
    obstacle = Obstacle(direction)
    obstacles.append(obstacle)

# 장애물 이동 및 제거
def move_obstacles():
    for obstacle in obstacles[:]:
        obstacle.move()
        if obstacle.rect.x < -50:
            obstacles.remove(obstacle)

    # 장애물 그리기
    for obstacle in obstacles:
        obstacle.draw()
# 게임 루프
def game_loop():
    player = Player()
    last_obstacle_time = 0  # 마지막 장애물 생성 시간
    isActive = True

    while isActive:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isActive = False

            # 오른쪽 버튼으로 흡기/호기 상태 전환
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                player.is_inhaling = not player.is_inhaling  # 상태 전환

        # 실시간 호흡 데이터 받아서 처리 (예: 딥러닝 예측)
        breath_data = collect_breath_data()
        mip, mep = predict_mip_mep(breath_data)

        # 캐릭터 위치 업데이트
        player.update_position()

        # 장애물 생성 (일정 시간 간격으로)
        current_time = pygame.time.get_ticks()
        if current_time - last_obstacle_time > 2000:
            create_obstacle()
            last_obstacle_time = current_time

        # 장애물 이동 및 충돌 체크
        move_obstacles()

        # 화면 업데이트
        SCREEN.fill(BLACK)  # 배경을 검정색으로
        SCREEN.blit(astronaut_img, astronaut_rect)  # 캐릭터 그리기
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

# 게임 실행
game_loop()
