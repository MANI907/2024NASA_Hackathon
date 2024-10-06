import sys  # 예측값 전달을 받기 위한 sys 모듈
import pygame
import os
import time
from pymongo import MongoClient
import random

# MongoDB 설정
client = MongoClient('mongodb://localhost:27017/')
db = client['GAMEDB']
scores_collection = db['scores']

# 프로젝트 절대 경로 가져오기
base_dir = os.path.dirname(os.path.abspath(__file__))

# 예측값 (predicted_mip)를 받아서 게임에 반영
predicted_mip = float(sys.argv[1]) if len(sys.argv) > 1 else 0
obstacle_speed = max(3, min(10, int(predicted_mip / 10)))

# 게임 화면 크기
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400

# 우주비행사 관련 설정
ASTRONAUT_WIDTH = 40
ASTRONAUT_HEIGHT = 60
astronaut_x = 100
astronaut_y = SCREEN_HEIGHT // 2 - ASTRONAUT_HEIGHT // 2

# 장애물 관련 설정
OBSTACLE_WIDTH = 180
OBSTACLE_HEIGHT = 200
obstacle_gap = 250
obstacles = []
last_obstacle_position = 'top'  # 마지막으로 배치된 장애물 위치 기억

# 게임 설정
pygame.init()
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Astronaut Obstacle Avoidance")

# 색상 설정
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# 배경 이미지 로드
background_image_path = os.path.join(base_dir, "static/images/background_obstacleMode.png")
background_image = pygame.image.load(background_image_path)
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
background_x1 = 0
background_x2 = SCREEN_WIDTH

# 우주비행사 이미지 로드
astronaut_image = pygame.image.load("player.jpg")
astronaut_image = pygame.transform.scale(astronaut_image, (ASTRONAUT_WIDTH, ASTRONAUT_HEIGHT))
astronaut_rect = astronaut_image.get_rect()
astronaut_rect.x = astronaut_x
astronaut_rect.y = astronaut_y

# 장애물 이미지 로드
obstacle_image_path = os.path.join(base_dir, "static/images/obstacle.png")
obstacle_image = pygame.image.load(obstacle_image_path)
obstacle_image_top = pygame.transform.scale(obstacle_image, (OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
obstacle_image_bottom = pygame.transform.rotate(obstacle_image_top, 180)

# 폰트 설정
font = pygame.font.SysFont("Arial", 55)
score_font = pygame.font.SysFont("Arial", 40)

# 점수 설정
start_time = time.time()

# 윗줄 장애물 생성 함수 (화면 최상단에 붙게)
def create_top_obstacle():
    global obstacles
    obstacle_x = SCREEN_WIDTH
    # 윗줄 장애물 (최상단에 고정된 위치로 장애물 생성)
    obstacles.append({
        "rect": pygame.Rect(obstacle_x, 0, OBSTACLE_WIDTH, OBSTACLE_HEIGHT),  # Y 좌표를 0으로 고정
        "image": obstacle_image_top
    })

# 아랫줄 장애물 생성 함수 (화면 최하단에 붙게)
def create_bottom_obstacle():
    global obstacles
    obstacle_x = SCREEN_WIDTH
    # 아랫줄 장애물 (최하단에 고정된 위치로 장애물 생성)
    obstacles.append({
        "rect": pygame.Rect(obstacle_x, SCREEN_HEIGHT - OBSTACLE_HEIGHT, OBSTACLE_WIDTH, OBSTACLE_HEIGHT),  # Y 좌표를 화면의 가장 아래로 고정
        "image": obstacle_image_bottom
    })

# 전체 장애물 생성 함수 (윗줄과 아랫줄이 엇갈리게 배치되도록)
def create_obstacles():
    if len(obstacles) == 0:
        # 윗줄 장애물 먼저 생성
        create_top_obstacle()
    else:
        # 마지막 장애물이 윗줄에 있으면 아랫줄 장애물 생성
        if obstacles[-1]['rect'].top == 0:
            create_bottom_obstacle()
        else:
            # 마지막 장애물이 아랫줄에 있으면 윗줄 장애물 생성
            create_top_obstacle()

# 장애물 이동 및 생성 함수
def move_obstacles():
    global obstacles
    for obstacle in obstacles[:]:
        obstacle["rect"].x -= obstacle_speed
        if obstacle["rect"].x < -OBSTACLE_WIDTH:
            obstacles.remove(obstacle)

    # 주기적으로 장애물 생성 (윗줄과 아랫줄 장애물을 번갈아가며 엇갈리게 생성)
    if len(obstacles) == 0 or obstacles[-1]['rect'].x < SCREEN_WIDTH - (OBSTACLE_WIDTH * 3):  # 장애물 간 간격 유지
        create_obstacles()

# 배경 이미지 이동 함수
def move_background():
    global background_x1, background_x2
    background_x1 -= obstacle_speed
    background_x2 -= obstacle_speed

    if background_x1 <= -SCREEN_WIDTH:
        background_x1 = SCREEN_WIDTH
    if background_x2 <= -SCREEN_WIDTH:
        background_x2 = SCREEN_WIDTH

# 우주비행사 이동 함수 (상하 키로 이동)
def move_astronaut(move_y):
    astronaut_rect.y += move_y

    if astronaut_rect.y < 0:
        astronaut_rect.y = 0
    if astronaut_rect.y > SCREEN_HEIGHT - ASTRONAUT_HEIGHT:
        astronaut_rect.y = SCREEN_HEIGHT - ASTRONAUT_HEIGHT

# 충돌 체크 함수
def check_collision():
    global is_game_over
    for obstacle in obstacles:
        if astronaut_rect.colliderect(obstacle["rect"]):
            is_game_over = True

# 점수 표시 함수
def show_score():
    current_time = time.time()
    score = int(current_time - start_time)
    score_text = score_font.render(f"Score: {score}", True, WHITE)
    SCREEN.blit(score_text, (10, 10))
    return score

# 게임 오버 메시지 표시
def show_game_over():
    game_over_text = font.render("GAME OVER", True, RED)
    SCREEN.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 30))

def show_start_delay():
    start_text = font.render("Game Starting in 3...", True, WHITE)
    SCREEN.fill(BLACK)
    SCREEN.blit(start_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 30))
    pygame.display.flip()
    pygame.time.wait(3000)  # 3초 대기

# 게임 루프
clock = pygame.time.Clock()
isActive = True
is_game_over = False
move_y = 0

show_start_delay()

while isActive:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isActive = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                move_y = -5
            if event.key == pygame.K_DOWN:
                move_y = 5
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                move_y = 0

    SCREEN.fill(BLACK)

    # 배경 그리기 (배경 이미지를 두 개로 스크롤)
    SCREEN.blit(background_image, (background_x1, 0))
    SCREEN.blit(background_image, (background_x2, 0))

    if not is_game_over:
        move_astronaut(move_y)
        move_obstacles()
        move_background()
        current_score = show_score()  # 현재 점수 표시
        check_collision()
    else:
        show_game_over()
        pygame.display.flip()
        pygame.time.wait(3000)  # 3초 대기
        isActive = False  # 루프 종료하여 게임 종료

    # 장애물 그리기
    for obstacle in obstacles:
        SCREEN.blit(obstacle["image"], obstacle["rect"])

    # 우주비행사 그리기
    SCREEN.blit(astronaut_image, astronaut_rect)

    pygame.display.flip()
    clock.tick(60)

# 게임 종료 시간과 경과 시간
end_time = time.time()
play_time_in_seconds = int(end_time - start_time)
game_end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))

# MongoDB에 스코어 데이터 저장
if is_game_over:
    score_data = {
        'score': current_score,
        'time_in_seconds': play_time_in_seconds,
        'game_end_time': game_end_time,
        'mode': 'o'
    }
    scores_collection.insert_one(score_data)
    print("점수 저장 완료:", score_data)

pygame.quit()
