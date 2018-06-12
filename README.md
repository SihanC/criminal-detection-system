# criminal-detection-system

## Description
This is a school project from CS 5412 cloud computing course at Cornell University. The project utilizes the concept of edge computing to design a criminal detection system for decreasing the latency of detecting criminals.

## Architecture
![alt text](https://github.com/SihanC/criminal-detection-system/blob/master/architecture.png "architecture")

Survilence cameras will extract pedestrian's faces from each frame it captured and send it to edge cache. Each edge cache equiped with a redis cache to store two sets of images, one set is criminal images uploaded by the local police department, the other set is citizen images received from the backend.
