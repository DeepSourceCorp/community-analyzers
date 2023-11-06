FROM python:3.11-alpine

RUN mkdir -p /home/runner /app /artifacts /toolbox \
  && chown -R 1000:3000 /home/runner /app /artifacts /toolbox \
  && chmod -R o-rwx /app /artifacts /toolbox \
  && adduser -D -u 1000 runner

RUN apk add --no-cache git grep

COPY . /toolbox/
# Change working dir to toolbox since we'd be invoking community analyzer from there.
WORKDIR /toolbox

# Install parser and the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

USER runner
