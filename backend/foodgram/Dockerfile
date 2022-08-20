FROM python:3.7-slim
COPY . .
RUN python -m pip install --upgrade pip
RUN pip3 install -r ./requirements.txt --no-cache-dir
WORKDIR /app
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]