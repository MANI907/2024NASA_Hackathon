import csv
import requests
import threading
import pygame
from pygame.rect import *
from pymongo import MongoClient
import random
from datetime import datetime

# 초기 coin_data 및 density에 따른 코인 개수 설정 함수
def get_coin_data(density):
    coin_data = []
    coin_count = max(int(density) % 5 + 3, 3)  # 최소 3개의 코인이 생성되도록 조정
    for i in range(coin_count):
        coin_data.append({
            "x": random.randint(800, 1200),  # 코인 생성 위치
            "y": random.randint(50, 350)
        })
    return coin_data

# 실시간 데이터 비동기 처리 함수
def fetch_data_in_background():
    while True:
        real_time_data = get_real_time_data()
        mag_data = get_magnetic_field_data()

        global current_real_time_data, current_mag_data
        if real_time_data:
            current_real_time_data = real_time_data
        if mag_data:
            current_mag_data = mag_data

        pygame.time.wait(5000)

def get_real_time_data():
    url = "https://services.swpc.noaa.gov/products/solar-wind/plasma-2-hour.json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data[1:]  # 첫 번째 요소는 헤더이므로 제외
        else:
            print("Failed to get data")
            return None
    except Exception as e:
        print(f"Error while fetching data: {e}")
        return None

def get_magnetic_field_data():
    url = "https://services.swpc.noaa.gov/products/solar-wind/mag-2-hour.json"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data[1:]  # 첫 번째 요소는 헤더이므로 제외
        else:
            print("Failed to get magnetic field data")
            return None
    except requests.Timeout:
        print("Request timed out")
        return None
    except Exception as e:
        print(f"Error while fetching magnetic field data: {e}")
        return None

# 자력계 데이터를 이용하여 플레이어 이동에 영향을 주는 함수
def apply_magnetic_field_effect(player_rect, bx_gsm, by_gsm):
    player_rect.x += int(bx_gsm / 100)
    player_rect.y += int(by_gsm / 100)

    if player_rect.x < 0:
        player_rect.x = 0
    if player_rect.x > SCREEN_WIDTH - player_rect.width:
        player_rect.x = SCREEN_WIDTH - player_rect.width
    if player_rect.y < 0:
        player_rect.y = 0
    if player_rect.y > SCREEN_HEIGHT - player_rect.height:
        player_rect.y = SCREEN_HEIGHT - player_rect.height

# 코인 위치 업데이트
def moveCoins(coin_rects, speed):
    move_speed = speed / 100
    for coin_rect in coin_rects:
        coin_rect.x -= move_speed
        if coin_rect.x < -coin_rect.width:
            coin_rect.x = SCREEN_WIDTH + random.randint(50, 200)
            coin_rect.y = random.randint(50, SCREEN_HEIGHT - 50)
        SCREEN.blit(coin_image, coin_rect)

# 게임 실행 시간 설정 (10초)
GAME_DURATION = 15000  # 15,000 milliseconds = 15 seconds

def restart():
    global score, isGameOver, rectCoin
    rectCoin = []
    real_time_data = get_real_time_data()
    if real_time_data:
        coin_data = get_coin_data(float(real_time_data[0][1]))
        for coin in coin_data:
            rect = coin_image.get_rect()
            rect.x = coin['x']
            rect.y = coin['y']
            rectCoin.append(rect)
    score = 0
    isGameOver = False

def eventProcess(move):
    global isActive
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isActive = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                isActive = False
            if event.key == pygame.K_UP:
                move.y = -5
            if event.key == pygame.K_DOWN:
                move.y = 5
            if event.key == pygame.K_r:
                restart()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                move.y = 0

def movePlayer(player, current, move, isGameOver):
    if not isGameOver:
        current.y += move.y

    if current.y > SCREEN_HEIGHT - current.height:
        current.y = SCREEN_HEIGHT - current.height
    if current.y < 0:
        current.y = 0
    SCREEN.blit(player, current)

def CheckCollision(player, coins):
    global isGameOver, score
    if isGameOver:
        return
    for coin in coins[:]:
        if coin.top < player.bottom and player.top < coin.bottom and coin.left < (player.right - 8) and (player.left + 8) < coin.right:
            score += 1
            coins.remove(coin)

def setText(isupdate=False, time_left=None):
    global score
    myFont = pygame.font.SysFont("arial", 20, True, False)
    score_text = myFont.render(f'Score : {score}', True, 'green')
    SCREEN.blit(score_text, (10, 10))
    if time_left is not None:
        time_text = myFont.render(f'Time Left: {time_left // 1000}s', True, 'green')
        SCREEN.blit(time_text, (10, 30))
    if isupdate:
        game_over_text = myFont.render(f'Game Over!!', True, 'red')
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        SCREEN.blit(game_over_text, game_over_rect)

# 게임 변수
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
score = 0
isActive = True
isGameOver = False
move = Rect(0, 0, 0, 0)
start_time = pygame.time.get_ticks()
current_real_time_data = None
current_mag_data = None

# pygame 초기화
pygame.init()
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Coin Collector!")

# 배경
background = pygame.image.load("background.png")
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# 플레이어
player = pygame.image.load("Player.jpg")
player = pygame.transform.scale(player, (20, 30))
rectPlayer = player.get_rect()
rectPlayer.centerx = 50
rectPlayer.centery = SCREEN_HEIGHT / 2

# 동전 이미지
coin_image = pygame.image.load("gas.png")
coin_image = pygame.transform.scale(coin_image, (20, 20))

# 초기 동전 위치 설정
rectCoin = []

# 비동기 데이터 처리 쓰레드 시작
data_thread = threading.Thread(target=fetch_data_in_background)
data_thread.daemon = True
data_thread.start()

# 코인을 주기적으로 추가 생성하는 함수
def generate_new_coins():
    global rectCoin
    real_time_data = get_real_time_data()
    if real_time_data:
        new_coin_data = get_coin_data(float(real_time_data[0][1]))
        for coin in new_coin_data:
            rect = coin_image.get_rect()
            rect.x = coin['x']
            rect.y = coin['y']
            rectCoin.append(rect)

# MongoDB에 점수와 게임 종료 시각을 저장하는 함수
def save_score_to_mongodb(score, time_in_seconds):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['GAMEDB']
    scores_collection = db['scores']

    # 현재 시각을 기록
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    score_data = {
        'score': score,
        'time_in_seconds': time_in_seconds,
        'game_end_time': current_time  # 게임 종료 시각 저장
    }
    scores_collection.insert_one(score_data)

# 서버에 점수와 상태를 업데이트하는 함수
def update_server_score(score):
    try:
        response = requests.post(f'http://127.0.0.1:5000/update_score/{score}')
        if response.status_code == 200:
            print("Server updated successfully with score!")
        else:
            print(f"Failed to update server: {response.status_code}")
    except Exception as e:
        print(f"Error while sending score to server: {e}")

# 게임 루프
clock = pygame.time.Clock()
while isActive:
    # 남은 시간 계산
    elapsed_time = pygame.time.get_ticks() - start_time
    time_left = GAME_DURATION - elapsed_time

    SCREEN.fill((0, 0, 0))
    SCREEN.blit(background, (0, 0))

    if current_real_time_data and current_mag_data:
        speed = float(current_real_time_data[0][2])
        moveCoins(rectCoin, speed)
        bx_gsm = float(current_mag_data[0][1])
        by_gsm = float(current_mag_data[0][2])
        apply_magnetic_field_effect(rectPlayer, bx_gsm, by_gsm)

    eventProcess(move)
    movePlayer(player, rectPlayer, move, isGameOver)
    CheckCollision(rectPlayer, rectCoin)

    # 게임이 끝났을 경우
    if time_left <= 0:
        isGameOver = True
        time_left = 0
        time_in_seconds = (pygame.time.get_ticks() - start_time) // 1000
        save_score_to_mongodb(score, time_in_seconds)  # 점수와 종료 시각을 저장
        update_server_score(score)  # 서버로 점수와 상태 전송
        setText(isGameOver, time_left)
        pygame.display.flip()  # 게임 오버 메시지 표시
        pygame.time.wait(5000)  # 5초 대기
        isActive = False  # 루프를 종료하여 게임 창을 닫게 함

    # 점수 및 남은 시간 텍스트 표시
    setText(isGameOver, time_left)

    if len(rectCoin) < 3:
        generate_new_coins()

    pygame.display.flip()
    clock.tick(60)

# 게임 종료 시 처리
pygame.quit()
quit()
