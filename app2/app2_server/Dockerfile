# set base image
FROM ubuntu:18.04

# install necessary packages
RUN apt-get update -y && apt-get install -y python3-pip \
    python3-dev \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglu1

# change pwd
COPY . /app
WORKDIR /app

# install pip packages
RUN bash install_dependencies.sh
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN python3 setup.py build_ext --inplace
RUN python3 aeneas_check_setup.py

# run application
ENTRYPOINT [ "python3" ]
CMD [ "app2_server.py" ]