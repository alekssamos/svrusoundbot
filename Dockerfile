FROM python:3.9-slim-buster

LABEL maintainer="alekssamos <aleks-samos@yandex.ru>" \
      description="sv-ru-sound TG Bot"

ENV TZ=Europe/Moscow

WORKDIR "/app"
VOLUME /app
COPY . /app
RUN python3 -m pip install --no-cache-dir -r requirements.txt
CMD ["python3", "svrusoundbot.py"]
