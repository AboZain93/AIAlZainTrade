FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ backend/
COPY ai_engine/ ai_engine/
COPY telegram/ telegram/
COPY database/ database/
COPY integration/ integration/
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
