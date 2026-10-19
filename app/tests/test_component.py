import pytest
import base64
import io
from PIL import Image
from unittest.mock import patch

from app.schemas import PredictionRequest, PredictionLabel, InvalidInputError, ModelInferenceError
from app.service import QualityInspectionService

def generate_test_image_base64() -> str:
    img = Image.new("RGB", (100, 100), color="black")
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

@pytest.fixture
def service():
    return QualityInspectionService()

def test_valid_request_returns_schema(service):
    img_b64 = generate_test_image_base64()
    req = PredictionRequest(item_id="ITEM_001", image_base64=img_b64, camera_id="CAM_1")
    with patch.object(service.model, 'predict', return_value=("NORMAL", 0.95)):
        result = service.process(req)
        assert result.item_id == "ITEM_001"
        assert result.prediction == PredictionLabel.NORMAL
        assert result.confidence == 0.95
        assert result.manual_review_required is False

def test_defect_with_low_confidence_triggers_review(service):
    img_b64 = generate_test_image_base64()
    req = PredictionRequest(item_id="ITEM_002", image_base64=img_b64, camera_id="CAM_1")
    with patch.object(service.model, 'predict', return_value=("DEFECT", 0.60)):
        result = service.process(req)
        assert result.prediction == PredictionLabel.DEFECT
        assert result.manual_review_required is True

def test_invalid_base64_raises_error(service):
    req = PredictionRequest(item_id="ITEM_003", image_base64="не_валидный_base64_123", camera_id="CAM_1")
    with pytest.raises(InvalidInputError):
        service.process(req)

def test_model_failure_raises_error(service):
    img_b64 = generate_test_image_base64()
    req = PredictionRequest(item_id="ITEM_004", image_base64=img_b64, camera_id="CAM_1")
    with patch.object(service.model, 'predict', side_effect=ModelInferenceError("GPU OOM")):
        with pytest.raises(ModelInferenceError):
            service.process(req)
