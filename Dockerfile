from python:3-alpine

COPY ./requirements.txt /app/requirements.txt
RUN set -eux; \
    apk add --virtual build_dependencies build-base; \
    apk add --no-cache libstdc++; \
    apk add postgresql-dev;  \
    apk add libffi-dev; \
    pip install --no-cache-dir -r /app/requirements.txt; \
    apk del build_dependencies;
COPY . /app
WORKDIR /app
ENTRYPOINT [ "python" ]
CMD [ "main.py" ]