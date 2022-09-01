FROM docker.io/python:3.10 AS build

WORKDIR /src

RUN pip install poetry
RUN poetry config virtualenvs.create false

COPY . .

RUN poetry build

FROM docker.io/python:3.10-slim

ARG wheel=yamlmerge-*-py3-none-any.whl

WORKDIR /app
COPY --from=build /src/dist/$wheel .
RUN pip install $wheel && rm $wheel

CMD ["/usr/local/bin/yamlmerge"]
