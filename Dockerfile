FROM alpine
LABEL maintainer="EGriffith92@gmail.com"
LABEL repository="https://github.com/egriffith/ElasticDNS"

WORKDIR /app/
RUN adduser -h /app -g ElasticDNS -s /sbin/nologin -S -H elasticdns
COPY ./VERSION src/entrypoint.sh src/requirements.txt src/elasticdns.ip src/elasticdns.py src/elasticdns.conf ./

RUN chown root:root * && chmod 755 * && chown elasticdns elasticdns.ip 

RUN apk add --no-cache python3 && pip3 --no-cache-dir install -r requirements.txt

USER elasticdns
ENTRYPOINT ["./entrypoint.sh"]
CMD ["-h"]