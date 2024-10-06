import sys  # 예측값 전달을 받기 위한 sys 모듈
import pygame
import os

# 프로젝트 절대 경로 가져오기
base_dir = os.path.dirname(os.path.abspath(__file__))

# 예측값 (predicted_mip)를 받아서 게임에 반영
if len(sys.argv) > 1:
    try:
        predicted_mip = float(sys.argv[1])  # 예측값 받아오기
    except ValueError:
        predicted_mip = 0  # 값이 잘못된 경우 기본값 설정
else:
    predicted_mip = 0  # 예측값이 없을 경우 기본값 설정

# predicted_mip 값을 이용해 장애물 속도나 빈도를 조정
# 예를 들어, predicted_mip가 높을수록 속도를 빠르게 설정
obstacle_speed = max(3, min(10, int(predicted_mip / 10)))  # 속도는 3~10 사이로 제한

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
obstacles = []

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
background_x1 = 0  # 첫 번째 배경의 x 위치
background_x2 = SCREEN_WIDTH  # 두 번째 배경의 x 위치 (첫 번째 배경 뒤에 위치)

# 우주비행사 이미지 로드
astronaut_image = pygame.image.load("player.jpg")
astronaut_image = pygame.transform.scale(astronaut_image, (ASTRONAUT_WIDTH, ASTRONAUT_HEIGHT))
astronaut_rect = astronaut_image.get_rect()
astronaut_rect.x = astronaut_x
astronaut_rect.y = astronaut_y  # 중간에서 시작

# 장애물 이미지 로드
obstacle_image_path = os.path.join(base_dir, "static/images/obstacle.png.png")
obstacle_image = pygame.image.load(obstacle_image_path)
obstacle_image_top = pygame.transform.scale(obstacle_image, (OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
obstacle_image_bottom = pygame.transform.rotate(obstacle_image_top, 180)  # 180도 회전

# 폰트 설정 (게임 오버 메시지)
font = pygame.font.SysFont(None, 55)

# 점수 설정
score = 0
score_font = pygame.font.SysFont(None, 40)

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
    global obstacles, score
    for obstacle in obstacles[:]:
        obstacle["rect"].x -= obstacle_speed
        if obstacle["rect"].x < -OBSTACLE_WIDTH:
            obstacles.remove(obstacle)
            score += 1  # 장애물 통과 시 점수 증가

    # 주기적으로 장애물 생성
    if len(obstacles) < 6:
        create_obstacles()

# 배경 이미지 이동 함수
def move_background():
    global background_x1, background_x2
    background_x1 -= obstacle_speed
    background_x2 -= obstacle_speed

    # 배경이 화면을 넘어가면 다시 원래 위치로 재설정
    if background_x1 <= -SCREEN_WIDTH:
        background_x1 = SCREEN_WIDTH
    if background_x2 <= -SCREEN_WIDTH:
        background_x2 = SCREEN_WIDTH

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

# 게임 오버 메시지 표시
def show_game_over():
    game_over_text = font.render("GAME OVER", True, RED)
    SCREEN.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 30))

# 점수 표시
def show_score():
    score_text = score_font.render(f"Score: {score}", True, WHITE)
    SCREEN.blit(score_text, (10, 10))

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
        move_background()  # 배경도 이동
        show_score()
    else:
        show_game_over()

    # 배경 그리기 (배경 이미지를 두 개로 스크롤)
    SCREEN.blit(background_image, (background_x1, 0))
    SCREEN.blit(background_image, (background_x2, 0))

    # 장애물 그리기
    for obstacle in obstacles:
        SCREEN.blit(obstacle["image"], obstacle["rect"])

    # 우주비행사 그리기
    SCREEN.blit(astronaut_image, astronaut_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
