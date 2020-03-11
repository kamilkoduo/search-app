FROM python:3.8

ENV PYTHONUNBUFFERED 1

EXPOSE 80

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD python web/main.py