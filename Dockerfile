FROM python:3.9-slim as builder

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

COPY requirements.txt /app/
COPY deps/CFPQ_Data /app/deps/CFPQ_Data

RUN apt-get update && apt-get install -y gcc python3-dev libgraphblas-dev
RUN pip3 install pygraphblas==5.1.8.0
RUN pip3 install -r requirements.txt
RUN cd deps/CFPQ_Data && python3 setup.py install

FROM python:3.9-slim

RUN apt update && apt install -y time git

COPY --from=builder /usr/local /usr/local

RUN echo 'echo Welcome to the CFPQ_PyAlgo Docker container!' >> /root/.bashrc \
    && echo 'echo "Run \`python3 -m cfpq_cli.run_all_pairs_cflr --help\` to see the usage message."' >> /root/.bashrc \
    && echo 'echo "Detailed documentation is available in the \`/app/docs/\` folder."' >> /root/.bashrc

WORKDIR /app
COPY . /app

ENTRYPOINT ["/bin/bash"]
