FROM python:3.11-alpine

RUN mkdir -p /home/runner /app /artifacts /toolbox \
  && chown -R 1000:3000 /home/runner /app /artifacts /toolbox \
  && chmod -R o-rwx /app /artifacts /toolbox \
  && adduser -D -u 1000 runner

RUN apk add git grep

ADD ./sarif-parser /toolbox/sarif-parser

RUN pip install /toolbox/sarif-parser

USER runner
