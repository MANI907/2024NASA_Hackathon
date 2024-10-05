import pygame
import requests
from flask import Flask, jsonify
from pymongo import MongoClient

# Flask 앱 설정
app = Flask(__name__)

# MongoDB 연결 설정
client = MongoClient('mongodb://localhost:27017/')
db = client['GAMEDB']
users_collection = db['users']  # 'obstacles' 컬렉션 선택
obstacles_collection = db['obstacles']  # 'obstacles' 컬렉션 선택

@app.route('/')
def home():
    return "Login Page for Game"

# 장애물 데이터를 가져오는 라우트
@app.route('/obstacles')
def get_obstacles():
    obstacles = list(obstacles_collection.find({}, {'_id': 0}))  # '_id' 제외한 데이터 가져오기
    return jsonify(obstacles)  # 데이터를 JSON으로 반환

if __name__ == '__main__':
    app.run(debug=True)

# Pygame 초기화
pygame.init()

# 게임 화면 크기
screen_width = 800
screen_height = 400
screen = pygame.display.set_mode((screen_width, screen_height))

# 색상 설정
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# 플레이어 설정
player_width = 40
player_height = 40
player_x = 50
player_y = screen_height - player_height - 50
player_speed = 5

# MongoDB에서 장애물 데이터 가져오기 (Flask 서버에서 가져옴)
response = requests.get('http://localhost:5000/obstacles')
obstacles_data = response.json()

# 장애물 설정
def create_obstacle(obstacle_data):
    return {"x": obstacle_data['x'], "y": obstacle_data['y'], "width": obstacle_data['width'], "height": obstacle_data['height']}

obstacles = [create_obstacle(obstacle) for obstacle in obstacles_data]

# 게임 루프 설정
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 키 입력 처리
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed
    if keys[pygame.K_UP]:
        player_y -= player_speed
    if keys[pygame.K_DOWN]:
        player_y += player_speed

    # 게임 화면을 흰색으로 채움
    screen.fill(WHITE)

    # 플레이어 그리기
    pygame.draw.rect(screen, BLACK, [player_x, player_y, player_width, player_height])

    # 장애물 그리기 및 이동
    for obstacle in obstacles:
        pygame.draw.rect(screen, RED, [obstacle["x"], obstacle["y"], obstacle["width"], obstacle["height"]])
        obstacle["x"] -= 5  # 장애물이 왼쪽으로 이동
        # 장애물이 화면을 벗어나면 다시 화면 오른쪽 끝으로 이동
        if obstacle["x"] < -obstacle["width"]:
            obstacle["x"] = screen_width

    pygame.display.flip()
    clock.tick(30)

pygame.quit()