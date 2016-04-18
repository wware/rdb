FROM ubuntu:14.04
MAINTAINER Will Ware <wware@alum.mit.edu>

RUN apt-get update -y
RUN apt-get install -y python-virtualenv python-pip git

RUN pip install https://github.com/wware/rdb/archive/master.zip

COPY templates /templates
COPY static /static
COPY go.py /

EXPOSE 5000
CMD ["/usr/bin/python", "/go.py"]
