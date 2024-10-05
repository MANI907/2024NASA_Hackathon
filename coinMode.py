import requests
import pygame
from pygame.rect import *
import random

# 동전 위치는 실시간 태양풍의 density와 temperature 활용하여 설정 (x, y 좌표로 배치)
coin_data = [
    {"x": 400, "y": 100},
    {"x": 600, "y": 200},
    {"x": 800, "y": 300},
    {"x": 1000, "y": 150},
    {"x": 1200, "y": 250}
]
def get_real_time_data():
    #url = "https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json"
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
    global score, isGameOver, bgX, start_time
    for i in range(len(coin_data)):
        rectCoin[i].x = coin_data[i]['x']  # 원래 위치로 초기화
        rectCoin[i].y = coin_data[i]['y']
    score = 0
    isGameOver = False
    bgX = 0  # 배경 초기화
    start_time = pygame.time.get_ticks()  # 게임 시작 시간 초기화

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
    global SCREEN_HEIGHT
    if not isGameOver:
        current.y += move.y
    #### 화면 경계 처리
    if current.y > SCREEN_HEIGHT - current.height:
        current.y = SCREEN_HEIGHT - current.height
    if current.y < 0:
        current.y = 0
    SCREEN.blit(player, current)
# #########################################################
# def moveBackground():
#     global bgX
#     # 배경을 왼쪽으로 이동시키고 화면을 벗어나면 다시 오른쪽에서 이동
#     bgX -= 2
#     if bgX <= -SCREEN_WIDTH:
#         bgX = 0
#
#     # 배경 이미지가 끊김 없이 이어지도록 출력
#     SCREEN.blit(background, (bgX, 0))
#     SCREEN.blit(background, (bgX + SCREEN_WIDTH, 0))
# #########################################################
# def moveCoins(current):
#     # 동전도 배경과 함께 왼쪽으로 이동
#     for i in range(len(current)):
#         current[i].x -= 2  # 배경과 같은 속도로 이동
#         if current[i].x < -current[i].width:
#             current[i].x = SCREEN_WIDTH + random.randint(50, 200)  # 화면 밖으로 나가면 오른쪽에서 다시 나타나게 설정
#         SCREEN.blit(coin[i], current[i])
# #########################################################
# 배경과 동전을 speed 값으로 함께 이동시키는 함수
def moveBackgroundAndCoins(speed, coin_rects):
    global bgX

    # speed 값을 이동 속도로 사용
    move_speed = speed / 100  # speed 값을 적절한 범위로 조정

    # 배경을 왼쪽으로 이동시키고 화면을 벗어나면 다시 오른쪽으로 이동
    bgX -= move_speed
    if bgX <= -SCREEN_WIDTH:
        bgX = 0
    SCREEN.blit(background, (bgX, 0))
    SCREEN.blit(background, (bgX + SCREEN_WIDTH, 0))

    # 동전도 같은 속도로 이동
    for i in range(len(coin_rects)):
        coin_rects[i].x -= move_speed
        if coin_rects[i].x < -coin_rects[i].width:
            coin_rects[i].x = SCREEN_WIDTH + random.randint(50, 200)  # 화면 밖으로 나가면 오른쪽에서 다시 나타나게 설정
        SCREEN.blit(coin[i], coin_rects[i])

# 게임 시간이 1분(60초)으로 설정 (밀리초 단위)
GAME_DURATION = 60000  # 60,000 milliseconds = 1 minute
def CheckCollision(player, coins):
    global isGameOver, score
    if isGameOver:
        return
    for rec in coins:
        if rec.top < player.bottom \
                and player.top < rec.bottom \
                and rec.left < (player.right-8) \
                and (player.left+8) < rec.right:
            score += 1  # 스코어 증가
            rec.x = -100  # 충돌한 동전 화면 밖으로 보내서 사라지게 처리
#########################################################
def setText(isupdate=False, time_left=None):
    global score
    myFont = pygame.font.SysFont("arial", 20, True, False)

    SCREEN.blit(myFont.render(
        f'score : {score}', True, 'green'), (10, 10, 0, 0))

    if time_left is not None:
        SCREEN.blit(myFont.render(
            f'Time Left: {time_left // 1000}', True, 'green'), (10, 30, 0, 0))

    if isupdate:
        SCREEN.blit(myFont.render(
            f'Game Over!!', True, 'red'), (150, 300, 0, 0))
        SCREEN.blit(myFont.render(
            f'press R - Restart', True, 'red'), (140, 320, 0, 0))
#########################################################
#########################################################

##1. 변수 선언
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
score = 0
isActive = True
isGameOver = False
move = Rect(0, 0, 0, 0)
bgX = 0  # 배경의 수평 위치
start_time = pygame.time.get_ticks()  # 게임 시작 시간
#########################################################
##2. 스크린
pygame.init()
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Coin Collector!")

## 배경 이미지
background = pygame.image.load("background.png")
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

#########################################################
##3. player
player = pygame.image.load("Player.jpg")
player = pygame.transform.scale(player, (20, 30))
rectPlayer = player.get_rect()
rectPlayer.centerx = 50  # 플레이어는 화면 왼쪽 고정
rectPlayer.centery = SCREEN_HEIGHT / 2  # 플레이어는 상하로만 움직임
#########################################################
##4. 동전 (x, y 데이터를 사용하여 초기 위치 설정)
coin = [pygame.image.load("coin.png") for i in range(len(coin_data))]
rectCoin = [None for i in range(len(coin))]
for i in range(len(coin)):
    coin[i] = pygame.transform.scale(coin[i], (20, 20))
    rectCoin[i] = coin[i].get_rect()
    rectCoin[i].x = coin_data[i]['x']
    rectCoin[i].y = coin_data[i]['y']

# 동전 좌표 업데이트
def moveCoins(current, data):
    update_coin_positions(current, data)  # 실시간 데이터를 이용해 좌표 업데이트
    for i in range(len(current)):
        SCREEN.blit(coin[i], current[i])



##5. time
clock = pygame.time.Clock()

# 게임 루프
while isActive:
    # 1. 화면 검정색으로 지우기
    SCREEN.fill((0, 0, 0))

    # 2. 경과 시간 계산
    elapsed_time = pygame.time.get_ticks() - start_time
    time_left = GAME_DURATION - elapsed_time

    # 시간이 다 되면 게임 종료
    if time_left <= 0:
        isGameOver = True
        setText(True)
        pygame.display.flip()
        continue

    # 3. 실시간 데이터 가져오기
    real_time_data = get_real_time_data()

    if real_time_data:
        # speed 값을 활용해 배경과 동전 이동
        speed = float(real_time_data[0][2])  # 첫 번째 데이터의 speed 값 사용
        moveBackgroundAndCoins(speed, rectCoin)

        # 이벤트 처리
        eventProcess(move)

        # 플레이어 이동
        movePlayer(player, rectPlayer, move, isGameOver)

        # 충돌 체크
        CheckCollision(rectPlayer, rectCoin)

        # 텍스트 업데이트
        setText(isGameOver, time_left)

        # 화면 업데이트
        pygame.display.flip()
        clock.tick(60)

