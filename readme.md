# AI-powered cloud usage controlling system in smart home environment
In a smart home environment, we are using cloud computing for powerful processing and storage of big data that are generated from IoT devices. Further we are also using Fog to handle the data in a more real time manner. Whenever we request for any service, the service provider take advantage of the resource available at fog and cloud. Fog resources are used to provide more real-time, sensitive services that require less computing and storage resources. On the other hand, cloud resources are used to keep the data (big data) for future purpose and process them. Sometimes, it is difficult to fulfil all SLA constraints only with the cloud resource and that's where the fog resource comes into the picture.

This thesis topic mainly focuses on efficient utilisation of cloud and fog resources. An AI model (most probably the DRL) needs to be developed to decide when to use fog computing and when to use cloud computing.

## DRL-based Service Placement
- [x] [Source Code](/drl_algorithm)
![alt text](/docs/figs/fig_drlarch.png)

## Experiment Applications

### 1) Application 1 - Deep learning based object classification using YOLOv3
- [x] [Client Side](/app1_yolo/app1_client/)
- [x] [Server Side](/app1_yolo/app1_server/)
- Testing scripts
	- curl -X POST -F image=@traffic.jpg 'http://$IP:$PORT/api/detect' --output traffic_yolo.png
![alt text](/docs/figs/fig4.png)

### 2) Application 2 - Text-audio synchronisation or forced alignment (Aeneas)
- [x] [Client Side](/app2_aeneas/app2_client/)
- [x] [Server Side](/app2_aeneas/app2_server/)
- Testing scripts
	- python3 -m aeneas.diagnostics
	- python3 setup.py build_ext --inplace
	- python3 aeneas_check_setup.py
	- curl -X POST -F audio=@p001.mp3 -F subtitle=@p001.xhtml 'http://$IP:$PORT/api/sync' --output p001.json
![alt text](/docs/figs/fig5.png)

### 3) Application 3 - Speech-to-text conversion (PocketSphinx)
- [x] [Client Side](/app3_pocketsphinx/app3_client/)
- [x] [Server Side](/app3_pocketsphinx/app3_server/)
- Testing scripts
	- curl -X POST -F audio=@p001.mp3 'http://$IP:$PORT/api/sync' --output output.txt
![alt text](/docs/figs/fig6.png)
