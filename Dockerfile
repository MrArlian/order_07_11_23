FROM python:3.11-alpine

RUN apk update && apk add --no-cache python3-dev build-base libffi-dev openssl-dev

WORKDIR /home/site
COPY . /home/site

RUN pip install -r requirements.txt

CMD [ "python", "app/main.py" ]