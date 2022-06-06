FROM python:3.10-alpine as intermediate

RUN apk update \
    && apk add curl gcc python3-dev musl-dev openssl-dev libffi-dev build-base

COPY requirements.txt .
RUN     mkdir /wheels \
        && python -m pip install --upgrade pip \
        && pip wheel -r requirements.txt --wheel-dir /wheels \
        && rm requirements.txt

FROM python:3.10-alpine
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_INDEX=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8
COPY --from=intermediate /wheels /wheels

COPY . /opt/app/
WORKDIR /opt/
RUN python -m pip install --upgrade pip
RUN pip install /wheels/* && rm -rf /wheels && pip uninstall --yes pip
RUN find / | grep -E "(__pycache__$)" | xargs rm -rf
RUN addgroup -S application && adduser -S application -G application -H
RUN chown application:application -R /opt/app/
CMD cd /opt/ && gunicorn 'app.main:create_app'  -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

