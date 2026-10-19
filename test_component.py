import pytest
import base64
import io
from PIL import Image
from unittest.mock import patch

from app.schemas import PredictionRequest, PredictionLabel, InvalidInputError, ModelInferenceError
from app.service import QualityInspectionService

# --- Вспомогательная функция для генерации тестовой картинки ---
def generate_test_image_base64() -> str:
    # Создаем простую черную картинку 100x100
    img = Image.new("RGB", (100, 100), color="black")
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# Фикстура: создаем сервис один раз для всех тестов
@pytest.fixture
def service():
    return QualityInspectionService()

# 1. Корректный запрос дает результат установленной схемы
def test_valid_request_returns_schema(service):
    img_b64 = generate_test_image_base64()
    req = PredictionRequest(item_id="ITEM_001", image_base64=img_b64, camera_id="CAM_1")
    
    # Подменяем работу нейросети, чтобы тест не зависел от весов
    with patch.object(service.model, 'predict', return_value=("NORMAL", 0.95)):
        result = service.process(req)
        
        assert result.item_id == "ITEM_001"
        assert result.prediction == PredictionLabel.NORMAL
        assert result.confidence == 0.95
        assert result.manual_review_required is False # 0.95 > 0.75
        assert result.model_version == "1.0.0"
        assert result.request_id is not None

# 2. Второй вход дает отличающееся поведение (дефект + низкая уверенность -> ручная проверка)
def test_defect_with_low_confidence_triggers_review(service):
    img_b64 = generate_test_image_base64()
    req = PredictionRequest(item_id="ITEM_002", image_base64=img_b64, camera_id="CAM_1")
    
    # Имитируем ситуацию, когда модель нашла дефект, но не уверена (0.60 < 0.75)
    with patch.object(service.model, 'predict', return_value=("DEFECT", 0.60)):
        result = service.process(req)
        
        assert result.prediction == PredictionLabel.DEFECT
        assert result.manual_review_required is True # Сработало бизнес-правило!

# 3. Неверное или пограничное значение обрабатывается контролируемым способом
def test_invalid_base64_raises_error(service):
    req = PredictionRequest(item_id="ITEM_003", image_base64="не_валидный_base64_123", camera_id="CAM_1")
    
    # Ожидаем нашу кастомную ошибку валидации
    with pytest.raises(InvalidInputError):
        service.process(req)

# 4. Сбой модели не приводит к ложному успешному результату
def test_model_failure_raises_error(service):
    img_b64 = generate_test_image_base64()
    req = PredictionRequest(item_id="ITEM_004", image_base64=img_b64, camera_id="CAM_1")
    
    # Имитируем падение модели (например, нехватка памяти)
    with patch.object(service.model, 'predict', side_effect=ModelInferenceError("GPU OOM")):
        with pytest.raises(ModelInferenceError):
            service.process(req)
