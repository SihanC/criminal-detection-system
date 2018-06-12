#! /bin/bash

# install requirement
apt-get -y update
apt-get install -y build-essential cmake
apt-get install -y libopenblas-dev liblapack-dev
apt-get install -y libx11-dev libgtk-3-dev
apt-get install -y python python-dev python-pip
apt-get install -y python3 python3-dev python3-pip

# Install requirements
#pip3 install --upgrade google-cloud==0.27.0
#pip3 install --upgrade google-api-python-client==1.6.2
#pip3 install --upgrade pytz==2013.7

# Setup python3 for Dataproc
#echo "export PYSPARK_PYTHON=python3" | tee -a  /etc/profile.d/spark_config.sh  /etc/*bashrc /usr/lib/spark/conf/spark-env.sh
#echo "export PYTHONHASHSEED=0" | tee -a /etc/profile.d/spark_config.sh /etc/*bashrc /usr/lib/spark/conf/spark-env.sh
#echo "spark.executorEnv.PYTHONHASHSEED=0" >> /etc/spark/conf/spark-defaults.conf

pip install redis
pip install numpy
pip install dlib
pip install pillow
pip install --upgrade pip
pip install opencv-python
pip install face_recognition 
