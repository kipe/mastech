FROM alpine:latest

RUN apk add --no-cache python3 git build-base bluez-dev linux-headers glib-dev && \
    pip3 install git+https://github.com/kipe/mastech.git influxdb

ADD initial /usr/src/bin/initial
ADD mastechlogger.py /usr/src/bin/mastechlogger.py

ENV PYTHONUNBUFFERED=1

CMD ["python3", "/usr/src/bin/mastechlogger.py"]
