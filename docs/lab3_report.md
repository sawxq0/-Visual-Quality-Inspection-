# Отчет по лабораторной работе № 3
## Реализация программного компонента системы искусственного интеллекта

**Тема проекта:** Система визуального контроля качества продукции (Visual Quality Inspection).
**Реализованный компонент:** Оркестрация бизнес-правил и инференс (`app.service.QualityInspectionService`).

### 1. Место на архитектурной схеме
Компонент реализует связку «Preprocessing -> Inference Engine -> Business Logic» (из компонентной диаграммы ЛР2). Он изолирован от FastAPI и представляет собой чистый Python-код для работы с изображениями.

### 2. Входной и выходной контракт
* **Вход (`PredictionRequest`):** `item_id` (строка), `image_base64` (строка), `camera_id` (строка).
* **Выход (`PredictionResult`):** `request_id` (UUID), `item_id`, `prediction` (DEFECT/NORMAL), `confidence` (float 0.0-1.0), `model_version`, `manual_review_required` (bool).

### 3. Используемая модель и алгоритм
* **Интеллектуальная функция:** Нейросеть MobileNetV3 (из библиотеки `torchvision`), модифицированная под 2 класса (DEFECT/NORMAL). Используется честный инференс на PyTorch (CPU).
* **Прикладное правило:** Если `confidence < 0.75`, флаг `manual_review_required` становится `True` (по требованию FR-03 из ЛР2).
* **Обработка ошибок:** При битом base64 вызывается `InvalidInputError`, при сбое модели — `ModelInferenceError`.

### 4. Команды для запуска
```bash
python -m venv .venv
source .venv/bin/activate # (или .venv\Scripts\activate.bat для Windows)
pip install -r requirements.txt
python -m pytest -q
