FROM python:2.7

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY requirements-run.txt ./
RUN pip install --no-cache-dir -r requirements-run.txt

COPY nginxauthdaemon nginxauthdaemon

EXPOSE 5000

CMD [ "gunicorn", "-b", "0.0.0.0:5000", "nginxauthdaemon:app" ]