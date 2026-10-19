from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

# Допустимые вердикты 
class PredictionLabel(str, Enum):
    DEFECT = "DEFECT"
    NORMAL = "NORMAL"

# Входной контракт
class PredictionRequest(BaseModel):
    item_id: str = Field(..., min_length=1, description="Уникальный идентификатор изделия")
    image_base64: str = Field(..., min_length=10, description="Изображение в формате base64")
    camera_id: str = Field(..., min_length=1, description="Идентификатор камеры")

# Выходной контракт
class PredictionResult(BaseModel):
    request_id: str = Field(..., description="Уникальный идентификатор запроса (UUIDv4)")
    item_id: str = Field(..., description="Идентификатор переданного объекта")
    prediction: PredictionLabel = Field(..., description="Текстовый вердикт (DEFECT / NORMAL)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Вероятность наличия дефекта")
    model_version: str = Field(..., description="Семантическая версия модели")
    manual_review_required: bool = Field(..., description="Флаг необходимости проверки оператором")
    defect_mask_url: Optional[str] = Field(default=None, description="Ссылка на маску дефекта")

# Явные ошибки (как требует лаба)
class InvalidInputError(Exception):
    """Вызывается при неверном входе"""
    pass

class ModelInferenceError(Exception):
    """Вызывается, если модель недоступна или упала"""
    pass
