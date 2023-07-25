# set base image
FROM ubuntu:18.04

# install necessary packages
RUN apt-get update -y && apt-get install -y python3-pip \
  python3-dev \ 
  libsm6 \
  libxext6 \
  libxrender-dev \
  libglu1 \
  wget

# change pwd
COPY . /app
WORKDIR /app

# install pip packages
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# run application
ENTRYPOINT [ "python3" ]
CMD [ "app3_server.py" ]
