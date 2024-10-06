import pygame
import math
import random

# 게임 화면 크기
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400

# 우주비행사 관련 설정
ASTRONAUT_WIDTH = 30
ASTRONAUT_HEIGHT = 30
astronaut_x = 100  # 우주비행사의 x 위치는 고정
astronaut_y = SCREEN_HEIGHT // 2 - ASTRONAUT_HEIGHT // 2  # y 위치는 화면의 중간

# 장애물 관련 설정
OBSTACLE_WIDTH = 80
OBSTACLE_HEIGHT = 40
obstacle_speed = 5
obstacles = []

# 게임 설정
pygame.init()
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Astronaut Obstacle Avoidance")

# 색상 설정
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# 우주비행사 이미지 로드
astronaut_image = pygame.image.load("player.jpg")
astronaut_image = pygame.transform.scale(astronaut_image, (ASTRONAUT_WIDTH, ASTRONAUT_HEIGHT))
astronaut_rect = astronaut_image.get_rect()
astronaut_rect.x = astronaut_x
astronaut_rect.y = astronaut_y  # 중간에서 시작

# 장애물 이미지 로드
obstacle_image = pygame.image.load("obstacle.png")
obstacle_image_top = pygame.transform.scale(obstacle_image, (OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
obstacle_image_bottom = pygame.transform.rotate(obstacle_image_top, 180)  # 180도 회전

# 장애물 생성 함수
def create_obstacles():
    global obstacles
    gap_size = 150  # 위아래 장애물 사이의 간격
    obstacle_x = SCREEN_WIDTH
    obstacle_y_top = 0  # 위쪽 장애물은 화면 위에 붙음
    obstacle_y_bottom = SCREEN_HEIGHT - OBSTACLE_HEIGHT  # 아래쪽 장애물은 화면 아래에 붙음

    # 위쪽 장애물
    obstacles.append({"rect": pygame.Rect(obstacle_x, obstacle_y_top, OBSTACLE_WIDTH, OBSTACLE_HEIGHT),
                      "image": obstacle_image_top})

    # 아래쪽 장애물
    obstacles.append({"rect": pygame.Rect(obstacle_x, obstacle_y_bottom, OBSTACLE_WIDTH, OBSTACLE_HEIGHT),
                      "image": obstacle_image_bottom})

# 장애물 이동 및 생성 함수
def move_obstacles():
    global obstacles
    for obstacle in obstacles[:]:
        obstacle["rect"].x -= obstacle_speed
        if obstacle["rect"].x < -OBSTACLE_WIDTH:
            obstacles.remove(obstacle)

    # 주기적으로 장애물 생성
    if len(obstacles) < 6:
        create_obstacles()

# 우주비행사 이동 함수 (상하 키로 이동)
def move_astronaut(move_y):
    astronaut_rect.y += move_y

    # 화면 경계 처리
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

# 게임 루프
clock = pygame.time.Clock()
isActive = True
is_game_over = False
move_y = 0

while isActive:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isActive = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                move_y = -5  # 위로 이동
            if event.key == pygame.K_DOWN:
                move_y = 5  # 아래로 이동
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                move_y = 0  # 키를 떼면 멈춤

    SCREEN.fill(BLACK)

    if not is_game_over:
        move_astronaut(move_y)
        move_obstacles()
        check_collision()

    # 장애물 그리기
    for obstacle in obstacles:
        SCREEN.blit(obstacle["image"], obstacle["rect"])

    # 우주비행사 그리기
    SCREEN.blit(astronaut_image, astronaut_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
