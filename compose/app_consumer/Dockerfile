FROM python:3.6

RUN apt-get update && apt-get install -y vim telnet \
    less build-essential git openssh-client supervisor libssl-dev libffi-dev && \
    apt-get clean && \
    mkdir -p /var/log/supervisor

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
COPY ./compose/app_consumer/supervisord.conf /etc/supervisord.conf
COPY ./chkinstreq.sh /app/chkinstreq.sh
RUN chmod +x /app/chkinstreq.sh

RUN pip3.6 install pip --upgrade && /app/chkinstreq.sh

ENV PYTHONUNBUFFERED 1

CMD supervisord -n -c /etc/supervisord.conf