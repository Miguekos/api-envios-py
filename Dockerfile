FROM python:3.8
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE=1

COPY . /app

WORKDIR /app

RUN pip install -r requeriment.txt

EXPOSE 9776

CMD [ "python" , "main.py" ]