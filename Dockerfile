FROM python:3-slim

RUN pip install --no-cache-dir pygithub

RUN apt-get update && apt-get -y install cron && apt-get clean

RUN apt-get -qqy update \
    && apt-get -qqy install cron\
    && apt-get -qyy clean \
    && apt-get -qyy autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /
COPY github-mirror.py /
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
