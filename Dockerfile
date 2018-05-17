FROM alpine
LABEL maintainer="EGriffith92@gmail.com"
LABEL repository="https://github.com/egriffith/ElasticDNS"

RUN apk update && apk add python3

WORKDIR /app/
COPY ./Version .
COPY src/requirements.txt .
COPY src/elasticdns.ip .
COPY src/elasticdns.py .

RUN chown root:root * && chmod 755 * && chown nobody:nobody elasticdns.ip

RUN pip3 install -r requirements.txt

USER nobody
ENTRYPOINT ["./elasticdns.py"]
CMD ["--iplog /app/elasticdns.ip --environmental"]