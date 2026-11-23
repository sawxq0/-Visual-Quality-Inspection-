import requests

BASE_URL = "http://localhost:8000"

def test_health():
    """Проверка доступности сервиса"""
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
    assert res.json()["model_version"] == "1.0.0"

def test_predict_invalid_data():
    """Проверка, что сервис не падает при неверных данных (ожидаем 422)"""
    payload = {
        "item_id": "", # Пустой ID, должен вызвать ошибку валидации
        "image_base64": "invalid_base64_string",
        "camera_id": "cam_01"
    }
    res = requests.post(f"{BASE_URL}/predict", json=payload)
    assert res.status_code == 422

def test_predict_valid_request():
    """Проверка успешного предсказания (отправляем валидный base64)"""
    # Очень маленькая картинка 1x1 пиксель в base64 (валидный формат)
    base64_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    payload = {
        "item_id": "item_123",
        "image_base64": base64_image,
        "camera_id": "cam_01"
    }
    
    res = requests.post(f"{BASE_URL}/predict", json=payload)
    
    # Ожидаем 200 OK, так как запрос валидный
    assert res.status_code == 200
    data = res.json()
    
    # Проверяем структуру ответа
    assert "request_id" in data
    assert "prediction" in data
    assert data["prediction"] in ["DEFECT", "NORMAL"]
    assert 0.0 <= data["confidence"] <= 1.0
