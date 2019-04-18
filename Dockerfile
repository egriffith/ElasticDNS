FROM alpine

RUN adduser -S -D -s /sbin/nologin -h /app elasticdns

COPY --chown=elasticdns:nogroup VERSION /app/
COPY --chown=elasticdns:nogroup src/requirements.txt /app/

RUN apk --update add --no-cache python3 && pip3 install --no-cache-dir -r /app/requirements.txt

COPY --chown=elasticdns:nogroup src/elasticdns.py /app/

USER elasticdns

VOLUME ["/var/log/elasticdns"]

ENTRYPOINT ["python3", "/app/elasticdns.py"]

CMD ["--container"]
