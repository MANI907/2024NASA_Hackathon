def get_user_data(username):
    # 임시로 고정된 사용자 데이터 예시
    if username == "user":
        return {
            'time': 100,  # 우주에 머문 시간 (예시)
            'gender': 1,  # 남성 (1), 여성 (0)
            'gravity': 0  # 중력 상태 (지구: 1, 무중력: 0)
        }
    return None
