import uuid
from app.schemas import PredictionRequest, PredictionResult, PredictionLabel
from app.preprocessing import prepare_image
from app.inference import DefectClassifier

class QualityInspectionService:
    def __init__(self):
        # Инициализируем нашу модель 
        self.model = DefectClassifier(model_version="1.0.0")
        self.confidence_threshold = 0.75

    def process(self, request: PredictionRequest) -> PredictionResult:
   
        
        # 1. Подготовка данных 
        tensor = prepare_image(request.image_base64)
        
        # 2. Вызов модели 
        label_str, confidence = self.model.predict(tensor)
        label = PredictionLabel(label_str)
        #ниже 0,75
        manual_review = False
        if confidence < self.confidence_threshold:
            manual_review = True
            
        # 4. Формируем типизированный результат
        return PredictionResult(
            request_id=str(uuid.uuid4()), # Генерируем уникальный ID запроса
            item_id=request.item_id,
            prediction=label,
            confidence=confidence,
            model_version=self.model.model_version,
            manual_review_required=manual_review,
            defect_mask_url=None # Пока оставляем None, так как сегментацию не делаем
        )
