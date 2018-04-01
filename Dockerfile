FROM python:latest

#WORKDIR /workdir

RUN apt-get update
RUN apt-get -y install libsodium-dev
COPY run.py requirements.txt ./
RUN pip install --trusted-host pypi.python.org -r requirements.txt

#CMD ["python", "-u", "run.py"]
