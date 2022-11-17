# AI-powered cloud usage controlling system in smart home environment

## Applications

### 1) Application 1 - Deep learning based object classification using YOLOv3
- [x] [Client Side](/app1/app1_client/)
- [x] [Server Side](/app1/app1_server/)
- [x] [System Architecture](/app1/app1.png)
- Testing scripts
	- curl -X POST -F image=@traffic.jpg 'http://$IP:$PORT/api/detect' --output traffic_yolo.png

### 2) Application 2 - Text-audio synchronisation or forced alignment (Aeneas)
- [ ] [Client Side](/app2/app2_client/)
- [ ] [Server Side](/app2/app2_server/)
- [x] [System Architecture](/app2/app2.png)
- Testing scripts
	- python3 -m aeneas.diagnostics
	- python3 setup.py build_ext --inplace
	- python3 aeneas_check_setup.py
	- curl -X POST -F audio=@p001.mp3 -F subtitle=@p001.xhtml 'http://$IP:$PORT/api/sync' --output p001.json

### 3) Application 3 - Speech-to-text conversion (PocketSphinx)
- [ ] [Client Side](/app3/app3_client/)
- [ ] [Server Side](/app3/app3_server/)
- [ ] [System Architecture](/app3/app3.png)



## Related papers are here:

- Chinmaya Kumar Dehury*, Satish Narayana Srirama; “An efficient service dispersal mechanism for fog and cloud computing using deep reinforcement learning”; The 20th IEEE/ACM International Symposium on Cluster, Cloud and Internet Computing (CCGRID2020), 11-14 May 2020, Melbourne, Australia

- Chinmaya Kumar Dehury, Satish Narayana Srirama, “Personalized Service Delivery using Reinforcement Learning in Fog and Cloud Environment”, The 21st International Conference on Information Integration and Web-based Applications & Services (iiWAS2019), 2-4 December 2019, Munich, Germany, pp 524-531, https://doi.org/10.1145/3366030.3366055
