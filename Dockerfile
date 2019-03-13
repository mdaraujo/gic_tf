FROM docker.io/ubuntu:16.04

ARG USE_PYTHON_3_NOT_2
ARG _PY_SUFFIX=${USE_PYTHON_3_NOT_2:+3}
ARG PYTHON=python${_PY_SUFFIX}
ARG PIP=pip${_PY_SUFFIX}

# See http://bugs.python.org/issue19846
ENV LANG C.UTF-8

RUN apt-get update && apt-get install -y \
    ${PYTHON} \
    ${PYTHON}-pip

RUN ${PIP} --no-cache-dir install --upgrade \
    pip \
    setuptools


# Some TF tools expect a "python" binary
RUN ln -s $(which ${PYTHON}) /usr/local/bin/python

ARG TF_PACKAGE=tensorflow
ARG TF_PACKAGE_VERSION=
RUN ${PIP} install ${TF_PACKAGE}${TF_PACKAGE_VERSION:+==${TF_PACKAGE_VERSION}}

####Corrigir se necessário
#COPY bashrc /etc/bash.bashrc
#RUN chmod a+rwx /etc/bash.bashrc

## Custom

#OpenCV
RUN apt-get install build-essential cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev -y

RUN ${PIP} install numpy opencv-python flask

RUN apt-get install wget -y

RUN mkdir -p /opt

RUN git clone https://github.com/mdaraujo/gic_tf.git /opt/yolo_tf
WORKDIR /opt/yolo_tf

RUN chmod +x drive_download.sh
RUN ./drive_download.sh

RUN mkdir weights
RUN mv YOLO_small.ckpt weights

EXPOSE 5000

CMD ["/usr/bin/python", "/opt/yolo_tf/yolo_tf_service.py"]
