FROM python:3.10-slim
WORKDIR /fast_api
COPY requirements.txt .
RUN pip install -r 'requirements.txt'
COPY . .
CMD uvicorn main:app --host 0.0.0.0 --port 8000