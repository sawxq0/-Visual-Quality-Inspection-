import base64
import io
import torch
from PIL import Image
from torchvision import transforms
from app.schemas import InvalidInputError

# Модели ожидают изображение 224x224 и нормализованные каналы RGB.
PREPROCESSING_PIPELINE = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],  # средние значения ImageNet
        std=[0.229, 0.224, 0.225]    # отклонения ImageNet
    )
])

def prepare_image(image_base64: str) -> torch.Tensor:
    """
    Принимает строку base64, возвращает тензор размером (1, 3, 224, 224).
    Если картинка битая — кидает InvalidInputError.
    """
    try:
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]
            
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Приводим к RGB (на случай, если картинка ч/б или с прозрачностью)
        image = image.convert("RGB")
        
    except Exception as e:
        # Ловим любые ошибки декодирования (битый base64, не картинка и т.д.)
        raise InvalidInputError(f"Не удалось прочитать изображение: {str(e)}")

    
    tensor = PREPROCESSING_PIPELINE(image).unsqueeze(0)
    
    return tensor
