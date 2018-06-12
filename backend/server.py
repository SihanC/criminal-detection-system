"""
Server program.

Receive images from Kafka and compare with backend criminal data
"""
import socket
import face_recognition
import numpy as np
from datetime import datetime
from io import BytesIO
from PIL import Image
from threading import Thread
from redis import StrictRedis
from twilio.rest import Client
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils


# choice to print time or send message with twilio
# 1 print time, 2 twilio
time_twilo = 1


def image_to_array(data):
    """
    Converting bytedata to image.

    Helper function for loading criminal images into an RDD. Taking in raw data
    and conver byte data to image.
    """
    path = str(data[0])
    name = path.split('-')[1]
    arr = np.asarray(Image.open(BytesIO(data[1])))
    return (name, arr)


def str_decoder(data):
    """
    Deserializer for key.

    The key is the ip address of the cache
    """
    return str(data.decode())


def nparray_decoder(data):
    """
    Deserializer for value.

    The value is an numpy array, the encoding
    """
    return np.fromstring(data)


def print_rdd(rdd):
    """
    Function used for tesing.

    Print out all the rdd values
    """
    for i in rdd.collect():
        print(i)


def parse_key(img):
    """
    Parsing incoming data.

    Incoming data contain edge cache ip and camer id.
    an example: "35.229.19.145-23"
    "35.229.19.145" is the ip address for the edge cache
    "23" is the camera id, that is the source of the image.
    """
    ip, camera_id = img[0].split('-')
    res = (ip, camera_id)

    return (res, img[1])


def check_criminal(img):
    """
    Compare face with criminal faces in local file system.

    Map incoming encoding into a tuple, with the first element be
    the result of the checking. 0 if not match with a criminal encoding
    1 otherwise.
    """
    result = 0
    name = ""
    for v in criminals.value:
        ecd = v[1]
        if face_recognition.compare_faces([ecd], img[1])[0] == 1:
            result = 1
            name = v[0]
            break
    return ((result, name), img)


def save_to_cache(rdd):
    """
    Save image to edge cache.

    If citizen, save its encoding to edge cache. Otherwise, sending alert.
    """
    for res, val in rdd.collect():
        url = val[0][0]
        camera_id = val[0][1]
        ecd = val[1]
        rds_criminal = StrictRedis(host=url, port=6379)

        if res[0] == 0:
            key = "nc_" + str(ecd)
            rds_criminal.set(key, ecd)
        else:
            name_lst = res[1].split('.')[0].split('_')
            name = name_lst[0] + " " + name_lst[1]
            if time_twilo == 1:
                print(datetime.utcnow())
                print("Alert!!! Criminal %s Found from camera %s" % (name, camera_id))
            else:
                message = client.messages.create(
                    to="+123456789",
                    from_="+123456789",
                    body="Alert!!! Criminal %s Found from camera %s" % (name, camera_id)
                )
                print(message)


def reload_images():
    """Reload the images, in case there is an addition."""
    images = sc.binaryFiles("gs://criminals")
    i_arr = images.map(image_to_array)
    l = []
    for v in i_arr.collect():
        x = face_recognition.face_encodings(v[1])[0]
        l.append((v[0], x))
    return l


class UpdateHandler(Thread):
    """Worker thread used to receive notification of reloading images."""

    def __init__(self):
        """Initialization of worker thread."""
        Thread.__init__(self)

    def run(self):
        """
        Main logic of the thread.

        If receive an message from administrator about a new criminal images is
        added, reload the images and rebrocast.
        """
        global criminals

        while True:
            try:
                conn, client_address = sock.accept()
                data = conn.recv(1024)
                if data.decode() == "update":
                    l = reload_images()
                    criminals.unpersist()
                    criminals = sc.broadcast(l)
            except:
                print("connection break")
                conn.close()
                break


# set up updating worker thread
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ("localhost", 20000)
print("starting up on %s port %s" % server_address)
sock.bind(server_address)
sock.listen(1)
print("waiting for a connection")
uh = UpdateHandler()
uh.start()

# setup twilio alert
account_sid = "abcd"    # dummy sid
auth_token = "abcd"     # dummy token
client = Client(account_sid, auth_token)

# load criminal images
conf = SparkConf()
sc = SparkContext(appName="CriminalRecognition")
sc.setLogLevel('WARN')

# loading criminal encodings
images = sc.binaryFiles("gs://criminals")
i_arr = images.map(image_to_array)
l = []
for v in i_arr.collect():
    x = face_recognition.face_encodings(v[1])[0]
    l.append((v[0], x))
criminals = sc.broadcast(l)

print("Finished loading images")

# setup Spark stream and fetch data from Kafka
topic = "encoding"
n_secs = 0.5
ssc = StreamingContext(sc, n_secs)
ip = "35.231.40.139:9092"
stream = KafkaUtils.createDirectStream(
    ssc, [topic], {
        'bootstrap.servers': ip,
        'fetch.message.max.bytes': '10000000',
        'auto.offset.reset': 'largest',
    }, keyDecoder=str_decoder, valueDecoder=nparray_decoder)

stream.map(parse_key).map(check_criminal).foreachRDD(save_to_cache)

ssc.start()
ssc.awaitTermination()
