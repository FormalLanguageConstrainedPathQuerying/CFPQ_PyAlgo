FROM python:3.9-slim AS builder

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

COPY requirements.txt /app/
COPY deps/CFPQ_Data /app/deps/CFPQ_Data

RUN apt-get update && apt-get install -y \
    python3-dev \
      git \
      wget \
      make \
      ninja-build \
      gcc \
      libomp-dev \
    && wget -qO- "https://cmake.org/files/v3.19/cmake-3.19.1-Linux-x86_64.tar.gz" \
      | tar --strip-components=1 -xz -C /usr/local
ENV GraphBLAS_ROOT=/usr/local
RUN cd deps \
    && git clone --depth 1 --branch vkutuev/kron https://github.com/vkutuev/GraphBLAS.git \
    && cmake -S ./GraphBLAS -B ./GraphBLAS/build -G Ninja -DCMAKE_INSTALL_PREFIX="$GraphBLAS_ROOT" \
    && cmake --build ./GraphBLAS/build \
    && cmake --install ./GraphBLAS/build
RUN pip install --no-binary suitesparse-graphblas suitesparse-graphblas==7.4.3
RUN pip3 install pygraphblas==5.1.8.0
RUN pip3 install -r requirements.txt
RUN cd deps/CFPQ_Data && python3 setup.py install

COPY . /app

ENTRYPOINT ["/bin/bash"]
