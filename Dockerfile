FROM python:latest

WORKDIR /app

ADD run.py /app

CMD ["python", "run.py"]
