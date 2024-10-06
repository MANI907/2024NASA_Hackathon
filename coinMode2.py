import csv
import requests
import threading
import pygame
from pygame.rect import *
from pymongo import MongoClient
import random

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
        # 데이터를 주기적으로 가져옴 (예: 5초마다)
        real_time_data = get_real_time_data()
        mag_data = get_magnetic_field_data()

        # 가져온 데이터를 사용할 수 있는 전역 변수로 업데이트
        global current_real_time_data, current_mag_data
        if real_time_data:
            current_real_time_data = real_time_data
        if mag_data:
            current_mag_data = mag_data

        # 데이터를 가져온 후 일정 시간 대기 (5초)
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
        response = requests.get(url, timeout=10)  # 타임아웃을 10초로 설정
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
    player_rect.x += int(bx_gsm / 100)  # x축 이동
    player_rect.y += int(by_gsm / 100)  # y축 이동

    # 화면 경계 처리
    if player_rect.x < 0:
        player_rect.x = 0
    if player_rect.x > SCREEN_WIDTH - player_rect.width:
        player_rect.x = SCREEN_WIDTH - player_rect.width
    if player_rect.y < 0:
        player_rect.y = 0
    if player_rect.y > SCREEN_HEIGHT - player_rect.height:
        player_rect.y = SCREEN_HEIGHT - player_rect.height

# 코인 위치 업데이트 (speed에 따른 이동)
def moveCoins(coin_rects, speed):
    move_speed = speed / 100  # speed 값에 따라 이동 속도 설정
    for coin_rect in coin_rects:
        coin_rect.x -= move_speed
        if coin_rect.x < -coin_rect.width:  # 화면을 벗어나면 오른쪽에서 다시 생성
            coin_rect.x = SCREEN_WIDTH + random.randint(50, 200)
            coin_rect.y = random.randint(50, SCREEN_HEIGHT - 50)
        SCREEN.blit(coin_image, coin_rect)

# 게임 시간이 1분(60초)으로 설정 (밀리초 단위)
GAME_DURATION = 10000  # 60,000 milliseconds = 1 minute

# 실시간 데이터를 동전 좌표로 변환하는 함수
def update_coin_positions(coin_rects, data):
    for i, entry in enumerate(data):
        if i < len(coin_rects):
            density = float(entry[1]) * 1000  # density 값을 x 좌표로 변환
            temperature = float(entry[3]) / 1000  # temperature 값을 y 좌표로 변환

            # 화면에 맞게 스케일 조정
            coin_rects[i].x = int(density) % SCREEN_WIDTH
            coin_rects[i].y = int(temperature) % SCREEN_HEIGHT

# 게임 시간이 1분(60초)으로 설정 (밀리초 단위)
GAME_DURATION = 60000  # 60,000 milliseconds = 1 minute

#########################################################
def restart():
    global score, isGameOver, rectCoin
    rectCoin = []
    real_time_data = get_real_time_data()
    if real_time_data:
        coin_data = get_coin_data(float(real_time_data[0][1]))  # density로 코인 개수 설정
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
        if event.type == pygame.QUIT:  # 윈도우 창을 닫을 때 처리
            isActive = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # ESC 키를 누르면 종료
                isActive = False
            if event.key == pygame.K_UP:
                move.y = -5  # 플레이어 위로 이동
            if event.key == pygame.K_DOWN:
                move.y = 5  # 플레이어 아래로 이동
            if event.key == pygame.K_r:
                restart()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                move.y = 0  # 키를 떼면 정지
#########################################################
def movePlayer(player, current, move, isGameOver):
    if not isGameOver:
        current.y += move.y  # move.y 값을 적용해 플레이어 이동

    # 화면 경계 처리
    if current.y > SCREEN_HEIGHT - current.height:
        current.y = SCREEN_HEIGHT - current.height
    if current.y < 0:
        current.y = 0
    SCREEN.blit(player, current)

# 배경을 고정하고 코인만 이동
def moveBackgroundAndCoins(speed, coin_rects):
    # speed 값을 이동 속도로 사용
    move_speed = speed / 100  # speed 값을 적절한 범위로 조정

    # 동전만 같은 속도로 이동
    for i in range(len(coin_rects)):
        coin_rects[i].x -= move_speed
        if coin_rects[i].x < -coin_rects[i].width:
            coin_rects[i].x = SCREEN_WIDTH + random.randint(50, 200)  # 화면 밖으로 나가면 오른쪽에서 다시 나타나게 설정
        SCREEN.blit(coin_image, coin_rects[i])
def CheckCollision(player, coins):
    global isGameOver, score
    if isGameOver:
        return
    for coin in coins[:]:  # coins 리스트의 복사본을 사용
        if coin.top < player.bottom and player.top < coin.bottom and coin.left < (player.right-8) and (player.left+8) < coin.right:
            score += 1  # 스코어 증가
            coins.remove(coin)  # 충돌한 코인을 리스트에서 제거
#########################################################
def setText(isupdate=False, time_left=None):
    global score
    myFont = pygame.font.SysFont("arial", 20, True, False)
    score_text = myFont.render(f'Score : {score}', True, 'green')
    SCREEN.blit(score_text, (10, 10))
    if time_left is not None:
        time_text = myFont.render(f'Time Left: {time_left // 1000}s', True, 'green')  # 초 단위로 표시
        SCREEN.blit(time_text, (10, 30))
    if isupdate:
        game_over_text = myFont.render(f'Game Over!!', True, 'red')
        restart_text = myFont.render(f'Press R - Restart', True, 'red')
        SCREEN.blit(game_over_text, (150, 300))
        SCREEN.blit(restart_text, (140, 320))

# game variables
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
score = 0
isActive = True
isGameOver = False
move = Rect(0, 0, 0, 0)
bgX = 0
start_time = pygame.time.get_ticks()
current_real_time_data = None
current_mag_data = None
#########################################################
# pygame init setting
pygame.init()
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Coin Collector!")

## background
background = pygame.image.load("background.png")
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

#########################################################
## player
player = pygame.image.load("Player.jpg")
player = pygame.transform.scale(player, (20, 30))
rectPlayer = player.get_rect()
rectPlayer.centerx = 50  # 플레이어는 화면 왼쪽 고정
rectPlayer.centery = SCREEN_HEIGHT / 2  # 플레이어는 상하로만 움직임
#########################################################
## coin image
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

# real_time_data = get_real_time_data()
# if real_time_data:
#     coin_data = get_coin_data(float(real_time_data[0][1]))  # density로 코인 개수 설정
#     for coin in coin_data:
#         rect = coin_image.get_rect()
#         rect.x = coin['x']
#         rect.y = coin['y']
#         rectCoin.append(rect)

## update coin position
# 코인 위치 업데이트 (speed에 따른 이동)
def moveCoins(coin_rects, speed):
    move_speed = speed / 50  # speed 값에 따라 이동 속도 설정
    for coin_rect in coin_rects:
        coin_rect.x -= move_speed
        if coin_rect.x < -coin_rect.width:  # 화면을 벗어나면 오른쪽에서 다시 생성
            coin_rect.x = SCREEN_WIDTH + random.randint(50, 200)
            coin_rect.y = random.randint(50, SCREEN_HEIGHT - 50)
        SCREEN.blit(coin_image, coin_rect)
def save_score_to_csv(score, time_in_seconds):
    with open('game_scores.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([score, time_in_seconds])

def save_score_to_mongodb(score, time_in_seconds):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['game_db']
    scores_collection = db['scores']

    score_data = {
        'score': score,
        'time_in_seconds': time_in_seconds
    }
    scores_collection.insert_one(score_data)

def send_score_to_server(score):
    try:
        response = requests.post('http://127.0.0.1:5000/save_score', json={'score': score})
        if response.status_code == 200:
            print("Score sent successfully!")
        else:
            print("Failed to send score:", response.status_code)
    except Exception as e:
        print(f"Error while sending score: {e}")

## time
clock = pygame.time.Clock()

# 게임 루프
while isActive:
    # 남은 시간 계산
    elapsed_time = pygame.time.get_ticks() - start_time  # 경과 시간
    time_left = GAME_DURATION - elapsed_time  # 남은 시간

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
        time_left = 0  # 시간이 음수로 내려가는 것을 방지
        # 게임 시간 계산
        time_in_seconds = (pygame.time.get_ticks() - start_time) // 1000

        # 파일에 저장하는 경우
        save_score_to_csv(score, time_in_seconds)

        # MongoDB에 저장하는 경우
        save_score_to_mongodb(score, time_in_seconds)

    # 점수 및 남은 시간 텍스트 표시
    setText(isGameOver, time_left)

    if len(rectCoin) < 3:  # 화면에 남은 코인이 적을 때 새로 생성
        generate_new_coins()

    pygame.display.flip()
    clock.tick(60)

# 게임이 종료되었을 때 호출
if isGameOver:
    time_in_seconds = (pygame.time.get_ticks() - start_time) // 1000
    send_score_to_server(score)  # 서버로 점수 전송

    pygame.quit()  # 게임 창 종료
    quit()  # 프로그램 완전히 종료