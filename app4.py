import pygame
from pygame.rect import *
import random

# 장애물 위치 데이터를 설정 (x, y 좌표로 배치)
obstacle_data = [
    {"x": 400, "y": 100},
    {"x": 600, "y": 200},
    {"x": 800, "y": 300},
    {"x": 1000, "y": 150},
    {"x": 1200, "y": 250}
]

#########################################################
def restart():
    global score, isGameOver, bgX
    for i in range(len(obstacle_data)):
        rectStar[i].x = obstacle_data[i]['x']  # 원래 위치로 초기화
        rectStar[i].y = obstacle_data[i]['y']
    score = 0
    isGameOver = False
    bgX = 0  # 배경 초기화

def eventProcess(move):
    global isActive
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
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
#########################################################
def moveBackground():
    global bgX
    # 배경을 왼쪽으로 이동시키고 화면을 벗어나면 다시 오른쪽으로 이동
    bgX -= 2
    if bgX <= -SCREEN_WIDTH:
        bgX = 0
    SCREEN.blit(background, (bgX, 0))
    SCREEN.blit(background, (bgX + SCREEN_WIDTH, 0))  # 끊김 없이 이어지게 배경 출력
#########################################################
def moveObstacles(current):
    # 장애물도 배경과 함께 왼쪽으로 이동
    for i in range(len(current)):
        current[i].x -= 2  # 배경과 같은 속도로 이동
        if current[i].x < -current[i].width:
            current[i].x = SCREEN_WIDTH + random.randint(50, 200)  # 화면 밖으로 나가면 오른쪽에서 다시 나타나게 설정
        SCREEN.blit(star[i], current[i])
#########################################################
def CheckCollision(player, star):
    global isGameOver, score
    if isGameOver:
        return
    for rec in star:
        if rec.top < player.bottom \
                and player.top < rec.bottom \
                and rec.left < (player.right-8) \
                and (player.left+8) < rec.right:
            isGameOver = True
            break
    score += 1
#########################################################
def setText(isupdate=False):
    global score
    myFont = pygame.font.SysFont("arial", 20, True, False)

    SCREEN.blit(myFont.render(
        f'score : {score}', True, 'green'), (10, 10, 0, 0))

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
#########################################################
##2. 스크린
pygame.init()
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rocket Dodge!")

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
##4. 장애물 (x, y 데이터를 사용하여 초기 위치 설정)
star = [pygame.image.load("star.png") for i in range(len(obstacle_data))]
rectStar = [None for i in range(len(star))]
for i in range(len(star)):
    star[i] = pygame.transform.scale(star[i], (20, 20))
    rectStar[i] = star[i].get_rect()
    rectStar[i].x = obstacle_data[i]['x']
    rectStar[i].y = obstacle_data[i]['y']
#########################################################
##5. time
clock = pygame.time.Clock()

while isActive:
    #1. 화면 검정색으로 지우기
    SCREEN.fill((0, 0, 0))
    #2. 배경 이동
    moveBackground()
    #3. 이벤트 처리
    eventProcess(move)
    #4. 플레이어 이동
    movePlayer(player, rectPlayer, move, isGameOver)
    #5. 장애물 이동
    moveObstacles(rectStar)
    #6. 충돌 체크
    CheckCollision(rectPlayer, rectStar)
    #7. 텍스트 업데이트
    setText(isGameOver)
    #8. 화면 업데이트
    pygame.display.flip()
    clock.tick(60)
