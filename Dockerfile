FROM alpine

RUN adduser --system --shell /bin/nologin --home /app elasticdns 

COPY --chown=elasticdns src/packages.apk /app/
COPY --chown=elasticdns src/elasticdns.py /app/

RUN apk add --no-cache $(cat /app/packages.apk)

USER elasticdns

ENTRYPOINT ["python3", "/app/elasticdns.py"]