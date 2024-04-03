# FROM python:3.10-slim as compiler
FROM quantconnect/lean as compiler
ENV PYTHONUNBUFFERED 1
RUN apt update && apt install python3-pip -y

WORKDIR /app/

RUN python -m venv /app/venv
# Enable venv
ENV PATH="/app/venv/bin:$PATH"

COPY ./requirements.txt /app/requirements.txt
# RUN pip install -Ur requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt


# FROM python:3.10-slim as runner
FROM quantconnect/lean as runner
WORKDIR /app/
COPY --from=compiler /app/venv /app/venv

# Enable venv
ENV PATH="/app/venv/bin:/Lean/Launcher/bin/Debug:$PATH"
ENV LEAN_PATH="/app/venv/bin/lean"

ENTRYPOINT []
COPY . /app/
# CMD ["uvicorn", "--app-dir", "./", "routes:app", "--reload"]
CMD python -m uvicorn --app-dir ./  --reload --host 0.0.0.0 --port 8000 routes:app
# gunicorn -w 2 -k unicornworkers.Unicornworker routes:app


# docker build -t sappv01 .
# docker run --rm -it -p 8000:8000 sappv01
# docker run --privileged=true -v /var/run/docker.sock:/var/run/docker.sock --rm -it -p 8000:8000 sappv01
# https://docker-fastapi-projects.readthedocs.io/en/latest/uvicorn.html
