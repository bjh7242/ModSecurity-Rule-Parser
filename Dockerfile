FROM ubuntu:16.04
MAINTAINER Chaim Sanders chaim.sanders@gmail.com

RUN apt-get update && \
  apt-get install -y python3 \
  python3-pip

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . /opt/

CMD ["python3", "/opt/start.py"]
