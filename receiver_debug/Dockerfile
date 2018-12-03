FROM python:3.7.1-stretch
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD ["python3","-u","receive.py"]
