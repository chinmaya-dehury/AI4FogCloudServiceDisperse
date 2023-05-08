# AI-powered cloud usage controlling system in smart home environment
In a smart home environment, we are using cloud computing for powerful processing and storage of big data that are generated from IoT devices. Further we are also using Fog to handle the data in a more real time manner. Whenever we request for any service, the service provider take advantage of the resource available at fog and cloud. Fog resources are used to provide more real-time, sensitive services that require less computing and storage resources. On the other hand, cloud resources are used to keep the data (big data) for future purpose and process them. Sometimes, it is difficult to fulfil all SLA constraints only with the cloud resource and that's where the fog resource comes into the picture.

This thesis topic mainly focuses on efficient utilisation of cloud and fog resources. An AI model (most probably the DRL) needs to be developed to decide when to use fog computing and when to use cloud computing.

## DRL-based Service Placement
- [x] [Source Code](/drl)
![alt text](/docs/figs/fig_drlarch.png)

## Experiment Applications

### 1) Application 1 - Deep learning based object classification using YOLOv3
- [x] [Client Side](/app1/app1_client/)
- [x] [Server Side](/app1/app1_server/)
- Testing scripts
	- curl -X POST -F image=@traffic.jpg 'http://$IP:$PORT/api/detect' --output traffic_yolo.png
![alt text](/docs/figs/fig4.png)

### 2) Application 2 - Text-audio synchronisation or forced alignment (Aeneas)
- [x] [Client Side](/app2/app2_client/)
- [x] [Server Side](/app2/app2_server/)
- Testing scripts
	- python3 -m aeneas.diagnostics
	- python3 setup.py build_ext --inplace
	- python3 aeneas_check_setup.py
	- curl -X POST -F audio=@p001.mp3 -F subtitle=@p001.xhtml 'http://$IP:$PORT/api/sync' --output p001.json
![alt text](/docs/figs/fig5.png)

### 3) Application 3 - Speech-to-text conversion (PocketSphinx)
- [x] [Client Side](/app3/app3_client/)
- [x] [Server Side](/app3/app3_server/)
- Testing scripts
	- curl -X POST -F audio=@p001.mp3 'http://$IP:$PORT/api/sync' --output output.txt
![alt text](/docs/figs/fig6.png)


## Usefull commands

### 1) Docker config

- sudo groupadd docker
- sudo usermod -aG docker $USER
- newgrp docker
- sudo chmod 666 /var/run/docker.sock
- sudo systemctl restart docker

### 2) Docker build, run, tag, service

- docker build -t $IMAGE_NAME:latest . 
- docker build -t $IMAGE_NAME -f $DOCKER_FILE_NAME .
- docker run -d -p 0:5000 $IMAGE_NAME:latest
- docker image tag $IMAGE_NAME:latest abbcyhn/$IMAGE_NAME:latest
- docker service create --name $IMAGE_NAME --replicas 1 --publish 0:5000 abbcyhn/$IMAGE_NAME
- docker service update --image abbcyhn/$IMAGE_NAME $IMAGE_NAME

### 3) Docker exec, logs

- docker exec -it $CONTAINER_NAME sh
- docker logs -f --tail 10 $CONTAINER_NAME

### 4) Python install, activate, deactivate "virtualenv"

- python3 -m pip install virtualenv
- python3 -m virtualenv env
- source env/bin/activate
- deactivate
- nohup python3 app1_server.py &
