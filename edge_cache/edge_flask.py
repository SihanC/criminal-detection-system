"""Edge Server."""
import numpy as np
import face_recognition
from flask import Flask
from flask import request
from kafka import KafkaProducer
from redis import StrictRedis
from datetime import datetime
from twilio.rest import Client


# setup flask
app = Flask(__name__)

# Kafka meta data
topic = "encoding"
kafka_ip = "35.231.40.139:9092"

# redis ip
ip = "35.231.228.39"

# redis connection
rds = StrictRedis(host=ip, port=6379)

# twilio
account_sid = "abcd"    # dummy account sid
auth_token = "abcd"     # dummy account token
client = Client(account_sid, auth_token)

# choice to print time or send message with twilio
# 1 print time, 2 twilio
time_twilo = 2


def send_to_kafka(cid, ecd):
    """
    Sending encoding to kafka.

    ecd is the encoding need to send to the Kafka
    """
    producer = KafkaProducer(
        bootstrap_servers=kafka_ip,
        max_request_size=10000000
    )

    key_str = ip + "-" + str(cid)
    # producer.send(topic, key=key_str.encode(), value=ecd.tobytes())
    print(producer.send(topic, key=key_str.encode(), value=ecd.tobytes()).get(timeout=30))


@app.route("/", methods=['POST'])
def main():
    """
    Main logic for the edge cache.

    Listen for connections from each camera and then create a handler for that.
    """
    content = request.json
    cid = content["id"]
    ecd_l = content["encoding"]
    ecd = np.array(ecd_l)

    # get all criminal encodings and compare
    for key in rds.scan_iter("c_*"):
        c_name = rds.get(key)
        key = key[3:]
        key = key[:-1]
        arr = np.fromstring(key, sep=' ')
        res = face_recognition.compare_faces([arr], ecd)[0]
        if res:
            if time_twilo == 1:
                print("criminal %s found on: ", c_name, datetime.utcnow())
            else:
                client.messages.create(
                    to="+123456789",        # dummy phone number
                    from_="+123456789",     # dummy phone number
                    body="Alert!!! Criminal %s Found from camera %s" % (c_name, cid)
                )
            return "Success"

    # get all citizen encodings stored and compare
    for key in rds.scan_iter("nc_*"):
        key = key[4:]
        key = key[:-1]
        arr = np.fromstring(key, sep=' ')
        res = face_recognition.compare_faces([arr], ecd)[0]
        if res:
            return "Success"

    # if not in the stored citizen send to kafka
    send_to_kafka(cid, ecd)

    return "Success"


if __name__ == '__main__':
    app.run(host="0.0.0.0")
