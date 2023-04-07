FROM python:3.10

ADD . /src
WORKDIR /src

ENV PYTHONUNBUFFERED 1

# This is required for crytography
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD python Main.py

