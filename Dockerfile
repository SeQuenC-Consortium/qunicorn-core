FROM python:3.11

# install git and remove caches again in same layer
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends git && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN useradd gunicorn


ENV FLASK_APP=qunicorn_core
ENV FLASK_ENV=development
ENV FLASK_DEBUG=0

# can be server or worker
ENV CONTAINER_MODE=server
ENV DEFAULT_LOG_LEVEL=INFO
ENV CONCURRENCY=2
ENV CELERY_WORKER_POOL=threads
ENV EXECUTE_CELERY_TASK_ASYNCHRONOUS=True
ENV RUNNING_IN_DOCKER=True

# make directories and set user rights
RUN mkdir --parents /app/instance \
    && chown --recursive gunicorn /app && chmod --recursive u+rw /app/instance

RUN python -m pip install poetry

COPY --chown=gunicorn . /app

RUN python -m poetry export --without-hashes --format=requirements.txt -o requirements.txt && python -m pip install -r requirements.txt

VOLUME ["/app/instance"]

EXPOSE 5005

USER gunicorn

ENTRYPOINT ["python","-m", "invoke", "start-docker"]
