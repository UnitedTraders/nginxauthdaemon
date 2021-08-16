FROM python:3.8-slim

LABEL maintainer="Anton Markelov <a.markelov@unitedtraders.com>"

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY requirements-run.txt ./
RUN pip install --no-cache-dir -r requirements-run.txt

COPY nginxauthdaemon nginxauthdaemon

RUN chgrp -R 0 /usr/src/app && \
  chmod -R g=u /usr/src/app && \
  useradd -u 1001 -g 0 nginxauthdaemon

USER 1001

EXPOSE 5000

CMD [ "gunicorn", "-b", "0.0.0.0:5000", "-k", "eventlet", "nginxauthdaemon:app" ]