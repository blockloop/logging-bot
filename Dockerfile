FROM pypy:3.7

WORKDIR /usr/src/bot

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "pypy3", "./app.py" ]
