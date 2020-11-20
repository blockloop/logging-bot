FROM python:3.8

WORKDIR /usr/src/bot
RUN pip install --no-cache-dir uwsgi

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3000
CMD ["uwsgi", "--socket", "0.0.0.0:3000", "--protocol=http", "--master", "-w", "wsgi:app"]
