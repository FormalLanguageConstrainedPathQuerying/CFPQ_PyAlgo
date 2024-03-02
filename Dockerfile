FROM python:3.9-slim as builder

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

COPY requirements.txt /app/
COPY deps/CFPQ_Data /app/deps/CFPQ_Data

RUN pip3 install pygraphblas==5.1.8.0
RUN pip3 install -r requirements.txt
RUN cd deps/CFPQ_Data && python3 setup.py install

FROM python:3.9-slim

RUN apt update
RUN apt install time

COPY --from=builder /usr/local /usr/local

WORKDIR /app
COPY . /app
