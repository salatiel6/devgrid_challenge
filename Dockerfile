# syntax=docker/dockerfile:1

FROM python:3.10.1

WORKDIR /app
COPY    requirements.txt ./

RUN pip install --no-cache-dir -U pip setuptools && \
    pip install -r requirements.txt

CMD ["python3", "app.py"]