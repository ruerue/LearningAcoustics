FROM python:3.7
RUN apt update -y && apt upgrade -y
RUN pip install pipenv
