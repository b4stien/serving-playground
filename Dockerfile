FROM python:3.11.1-bullseye@sha256:b86507b0c9d182edf164752715e0016184f9972495e670a9218b036ec154529a

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    haproxy \
    && rm -rf /var/lib/apt/lists/*

ADD requirements.txt /opt/serving-playground/requirements.txt
RUN pip install -r /opt/serving-playground/requirements.txt

ADD . /opt/serving-playground

RUN mkdir /var/run/fake_api/

LABEL "com.datadoghq.ad.check_names"='["haproxy"]'
LABEL "com.datadoghq.ad.init_configs"='["{}"]'
LABEL "com.datadoghq.ad.instances"='[{"use_openmetrics":"true", "openmetrics_endpoint": "http://%%host%%:27002/metrics"}]'

CMD [ "supervisord", "-c", "/opt/serving-playground/supervisord.conf" ]
