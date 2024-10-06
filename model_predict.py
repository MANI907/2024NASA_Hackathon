import numpy as np
from tensorflow.keras.models import load_model

# 학습된 모델 불러오기
model = load_model('models/my_model.keras')

# MIP 예측 함수
def predict_mip(user_data):
    time = np.exp(-0.00062 * np.array([user_data['time']]))
    gender = np.array([user_data['gender']])
    gravity = np.array([user_data['gravity']])
    input_data = np.column_stack((time, gender, gravity))

    # MIP 예측
    prediction = model.predict(input_data)
    return prediction[0][0]
