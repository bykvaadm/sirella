FROM python:3.13.12-slim-trixie
LABEL authors="a.kondratev"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && \
    apt install -y bind9 bind9utils bind9-dnsutils nano procps && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /etc/bind/zones

COPY app/bind/named.conf /etc/bind/named.conf
COPY app/bind/zones/ /etc/bind/zones/
COPY app/whois/whois-server.py /
COPY init.sh /

CMD ["/init.sh"]
