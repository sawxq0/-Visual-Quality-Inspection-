import base64
import io
import uuid
from contextlib import asynccontextmanager

import torch
from fastapi import FastAPI, HTTPException
from PIL import Image
from torchvision import transforms

from app.inference import DefectClassifier
from app.schemas import (
    PredictionRequest, 
    PredictionResult, 
    PredictionLabel, 
    InvalidInputError, 
    ModelInferenceError
)


classifier = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global classifier
    classifier = DefectClassifier(model_version="1.0.0")
    yield
    classifier = None

app = FastAPI(
    title="Visual Quality Inspection API", 
    version="1.0.0", 
    lifespan=lifespan
)


transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406], 
        std=[0.229, 0.224, 0.225]
    )
])

@app.get("/health")
def health():
    return {"status": "ok", "model_version": "1.0.0"}

@app.post("/predict", response_model=PredictionResult)
def predict(req: PredictionRequest):
    try:
       
        try:
            image_data = base64.b64decode(req.image_base64)
            image = Image.open(io.BytesIO(image_data)).convert("RGB")
        except Exception:
            raise InvalidInputError("Не удалось декодировать изображение из base64")

       
        tensor = transform(image).unsqueeze(0) # добавляем batch dimension

        label_str, confidence = classifier.predict(tensor)
        
     
        return PredictionResult(
            request_id=str(uuid.uuid4()),
            item_id=req.item_id,
            prediction=PredictionLabel(label_str),
            confidence=confidence,
            model_version=classifier.model_version,
            manual_review_required=(confidence < 0.7), # логика: если уверенность низкая, нужен человек
            defect_mask_url=None
        )

    except InvalidInputError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ModelInferenceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")
