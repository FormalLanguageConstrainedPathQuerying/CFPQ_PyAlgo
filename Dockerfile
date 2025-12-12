FROM python:3.9-slim

ADD . /CFPQ_PyAlgo

RUN apt update \
    && apt install -y \
      git \
      wget \
      make \
      gcc \
      libomp-dev \
    && wget -qO- "https://cmake.org/files/v3.19/cmake-3.19.1-Linux-x86_64.tar.gz" \
      | tar --strip-components=1 -xz -C /usr/local


WORKDIR /CFPQ_PyAlgo
RUN git submodule update --init

# ENV GraphBLAS_ROOT=/usr/local
# WORKDIR /usr/local
# COPY GraphBLAS_v743/Include /usr/local/include
# COPY GraphBLAS_v743/build_release/*.so /usr/local/lib/
# RUN ldconfig
ENV GraphBLAS_ROOT=/usr
WORKDIR /CFPQ_PyAlgo/deps/GraphBLAS/build
RUN cmake .. -DCMAKE_INSTALL_PREFIX=/usr \
    && make -j$(nproc) \
    && make install

RUN pip install --no-binary suitesparse-graphblas==5.1.3.0 suitesparse-graphblas==5.1.3.0

WORKDIR /CFPQ_PyAlgo/deps/CFPQ_Data
RUN python3 setup.py install

WORKDIR /CFPQ_PyAlgo
RUN pip3 install -r requirements.txt

