ARG PYTHON_VERSION=3.10


FROM python:${PYTHON_VERSION}-alpine AS build

RUN mkdir -p /code
COPY . /code
WORKDIR /code

RUN apk update \
    && apk add --no-cache gettext

RUN pip install pdm \
    && pdm sync --no-self \
    && pdm export -o requirements.txt

RUN pdm run manage.py compilemessages --ignore=.venv/* \
    && pdm run manage.py collectstatic --noinput


FROM python:${PYTHON_VERSION}-alpine AS run

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY --from=build /code .

RUN pip install -r requirements.txt \
    && chmod +x ./bin/release.sh \
    && chmod +x ./bin/launch.sh

EXPOSE 8080

CMD ["./bin/launch.sh"]
