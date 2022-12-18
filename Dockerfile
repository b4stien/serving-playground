FROM python:3.11.1-bullseye@sha256:b86507b0c9d182edf164752715e0016184f9972495e670a9218b036ec154529a

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    haproxy \
    && rm -rf /var/lib/apt/lists/*



ADD requirements.txt /opt/serving-playground/requirements.txt
RUN pip install -r /opt/serving-playground/requirements.txt

ADD . /opt/serving-playground

RUN mkdir /var/run/fake_api/

RUN wget https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v0.67.0/otelcol-contrib_0.67.0_linux_amd64.deb && dpkg -i otelcol-contrib_0.67.0_linux_amd64.deb

CMD [ "supervisord", "-c", "/opt/serving-playground/supervisord.conf" ]
