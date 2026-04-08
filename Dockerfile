FROM python:3.12

WORKDIR /app

COPY requirements-hf.txt .

RUN pip install -r requirements-hf.txt

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"

CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]