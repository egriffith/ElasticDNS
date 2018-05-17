FROM alpine
LABEL maintainer="EGriffith92@gmail.com"
LABEL repository="https://github.com/egriffith/ElasticDNS"

WORKDIR /app/
COPY ./Version src/requirements.txt src/elasticdns.ip src/elasticdns.py src/elasticdns.conf ./

RUN chown root:root * && chmod 755 * && chown nobody:nobody elasticdns.ip 

RUN apk add --no-cache python3 && pip3 --no-cache-dir install -r requirements.txt

USER nobody
#ENTRYPOINT ["./elasticdns.py"]
CMD ["./elasticdns.py"]