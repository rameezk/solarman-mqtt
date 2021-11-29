FROM python:3.9-alpine

RUN mkdir /app
WORKDIR /app

COPY requirements.txt .
RUN pip install -U pip && pip install -r requirements.txt

COPY entrypoint.sh run.py ./
COPY solarman_mqtt /app/solarman_mqtt

RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

ENTRYPOINT ["./entrypoint.sh"]