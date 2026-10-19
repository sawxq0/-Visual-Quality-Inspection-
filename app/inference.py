import torch
import torch.nn as nn
from torchvision import models
from app.schemas import ModelInferenceError

class DefectClassifier:
    def __init__(self, model_version: str = "1.0.0"):
        self.model_version = model_version
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        try:
            # 1. Загружаем предобученный backbone 
            self.model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT)
            
            # 2. Замораживаем веса 
            for param in self.model.parameters():
                param.requires_grad = False
                
            # 3. Заменяем последний слой (классификатор) на свой (2 класса: DEFECT и NORMAL)
            num_features = self.model.classifier[3].in_features
            self.model.classifier[3] = nn.Linear(num_features, 2)
            
            self.model.eval()
            self.model.to(self.device)
            
        except Exception as e:
            raise ModelInferenceError(f"Не удалось загрузить модель: {str(e)}")

    def predict(self, tensor: torch.Tensor) -> tuple[str, float]:
 
        try:
            tensor = tensor.to(self.device)
            
            with torch.no_grad():
                outputs = self.model(tensor)
                
                # Применяем Softmax, чтобы получить вероятности от 0 до 1
                probabilities = torch.softmax(outputs, dim=1)[0]
                
                # Берем класс с наибольшей вероятностью
                confidence, predicted_idx = torch.max(probabilities, 0)
                
                # Наша логика: 0 - это DEFECT, 1 - это NORMAL
                if predicted_idx.item() == 0:
                    label = "DEFECT"
                else:
                    label = "NORMAL"
                    
                return label, confidence.item()
                
        except Exception as e:
            raise ModelInferenceError(f"Ошибка во время инференса: {str(e)}")
