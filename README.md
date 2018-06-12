# criminal-detection-system

## Description
This is a school project from CS 5412 cloud computing course at Cornell University. The project utilizes the concept of edge computing to design a criminal detection system for decreasing the latency of detecting criminals.

## Architecture
![alt text](https://github.com/SihanC/criminal-detection-system/blob/master/architecture.png "architecture")

The architecture of the system is composed of three different layers as shown in figure above. At the first layer, we have surveillance cameras continuously capturing live video streams and sending image frames extracted from the live video into edge cache. Each edge server has a redis cache, which contains most wanted criminal images uploaded from local police department based on the local criminal priority and citizen images sent back from the backend, which are images previously sent by the edge cache to the backend and does not have any match with criminals stored in the backend storage system. The non-criminal data are stored based on a LRU scheme and this is stored mainly to prevent overloading the backend with too many requests. Since normally a person needs around 10 seconds to walk out of the area which a camera can capture, there will be multiple frames of the same person sent to the backend. In addition, a person captured by a camera is very likely to be captured by another camera in the area again. By storing the latest captured citizen images into redis will help filter out unnecessary image frames and reduce the load of the backend. 


## Implementation
Layer 1: Cameras were simulated by reading premade video stored in the personal laptop. Videos were first extracted into multiple single frames at 0.5 fps, then opencv library was used to detect and extract faces inside each frame and encode the image with face_recognition library and send to the edge through an HTTP request with the image encoding and the camera id. Zookeeper was used for distributed coordination and network discovery. Each edge server registers itself with the zookeeper during start up. The edge ip and the edge location were stored in the zookeeper nodes. The client has watchers to notify any change in the zookeeper nodes and routes the client to the nearest edge server.

Layer 2 (Edge Servers): All edge caches were hosted on Google Cloud. Each edge has a redis cache. Image encodings of most wanted criminals were added by the police department using the provided user interface. The non criminal images added by the backend. Each edge cache will continuously receive image encodings from cameras and compare them with criminal images stored by the police department and the citizen encodings added by the backend. If a match with the criminal image found, a twilio message will be sent to the police department along with the location of the criminal. If a match found with one of the citizen image, this encoding will be discarded. If the received image does not match with any of the criminal or citizen images, this image along with the edge ip and the camera id will be added to the Kafka, which was hosted on Google Cloud. 

Layer 3 (Backend): On the backend, Spark streaming was used to process incoming data stream reading from Kafka. Spark cluster was hosted on Google Dataproc. Each image reading from the live data stream was compared with all the images stored at the backend, which is on Google Cloud Storage. If a match found, then a twilio message will be sent to the police department. If no match found, the encoding of the image will be added to the redis at the edge where the image was originally sending from.
