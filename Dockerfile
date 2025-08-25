FROM python:3.13

ADD main.py .

ADD tokens.db .

ADD tokens.db-shm .

ADD tokens.db-wal .

RUN pip install -U twitchio --pre asqlite twitchio[starlette] obsws-python gtts boto3

USER $APP_UID:$APP_GUID

CMD ["python", "./main.py"]
