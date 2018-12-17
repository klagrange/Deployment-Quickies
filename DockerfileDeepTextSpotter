FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
      cpio \
      build-essential \
      cmake \
      git \
      wget \
      ssh \
      openssh-server \
      numactl \
      vim \
      net-tools \
      iputils-ping \
      screen \
      libmlx4-1 libmlx5-1 ibutils  rdmacm-utils libibverbs1 ibverbs-utils perftest infiniband-diags \
      openmpi-bin libopenmpi-dev \
      ufw \
      iptables \
      libboost-all-dev \
      libgflags-dev \
      libgoogle-glog-dev \
      libhdf5-serial-dev \
      libleveldb-dev \
      liblmdb-dev \
      libopencv-dev \
      libprotobuf-dev \
      libsnappy-dev \
      protobuf-compiler \
      python-dev \
      python-numpy \
      python-pip \
      python-setuptools \
      python-scipy && \
      rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get --yes install libatlas-base-dev

WORKDIR /app

# Install openCV
RUN git clone https://github.com/opencv/opencv.git && \
cd opencv && git checkout 3.4 && \
mkdir release && \
cd release && \
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local .. && \
make && \
make install

# Install Caffe Darknet
RUN git clone https://github.com/MichalBusta/caffe.git
RUN cd caffe && \
git checkout darknet && \
mkdir build && cd build && \
cmake -D BUILD_SHARED_LIBS=On .. && \
make

RUN apt-get install -y --no-install-recommends \
python-matplotlib python-numpy python-pil python-scipy \
build-essential cython \
python-skimage

RUN pip install protobuf

# Install DeepTextSpotter
RUN git clone https://github.com/MichalBusta/DeepTextSpotter.git && \
cd DeepTextSpotter && \
mkdir build && cd build && \
cmake .. && make

ENV PYTHONPATH="/app/caffe/python:/app/DeepTextSpotter/build/:$PYTHONPATH"






