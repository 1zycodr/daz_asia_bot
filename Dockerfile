FROM python:3.12

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean

WORKDIR /app

COPY venv /app/venv

ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY . /app/

EXPOSE 8080

CMD ["/app/venv/bin/python", "core/manage.py", "runserver", "0.0.0.0:8080"]

