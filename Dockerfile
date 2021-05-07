FROM graphblas/pygraphblas-minimal:v4.2.2

ADD . /CFPQ_PyAlgo

WORKDIR /CFPQ_PyAlgo
RUN git submodule init
RUN git submodule update

WORKDIR /CFPQ_PyAlgo/deps/CFPQ_Data
RUN python3 setup.py install

WORKDIR /CFPQ_PyAlgo
RUN pip3 install -r requirements.txt
