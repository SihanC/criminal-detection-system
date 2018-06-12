"""Camera."""
import cv2
import sys
import requests
import face_recognition
from datetime import datetime
from kazoo.client import KazooClient


image_path = "./output_frames"
video_path = ""
v_name = ""
url = ""
edge_ip = ""
camera_id = -1
# new edge ip is setted
set_flag = 0
zk = KazooClient(hosts='35.196.211.79,35.196.72.183,35.231.97.79')
# for testing, frame #
printlst = [0, 1, 2, 3, 4, 225, 226, 227, 228, 229]


@zk.ChildrenWatch('/cs5412')
def my_func(children):
    """
    Find the ip of the nearst available edge.

    send request to zookeeper and find out the nearest available edge
    to connect to.
    """
    global edge_ip, set_flag

    min_dist = 99999
    ip = ""
    for c in children:
        if c is not None:
            data, stat = zk.get("/cs5412/" + c)
            data = data.decode().split('-')
            ip = data[0]
            num = int(data[1])
            if min_dist > abs(camera_id - num):
                edge_ip = "http://" + ip + ":5000"
                min_dist = abs(camera_id - num)
    set_flag = 1
    print("new ip", edge_ip)


def send_img(img, count):
    """
    Sending image to edge cache.

    First connect to zookeeper and find out the nearest client, and then
    send the encoding to that edge through a HTTP request.
    """
    global url, camera_id, set_flag, edge_ip

    ecd = face_recognition.face_encodings(img)
    if ecd != []:
        data = {"id": camera_id, "encoding": list(ecd[0])}
        if v_name == "criminals" and count in printlst:
            print("sending image time", v_name, datetime.utcnow(), count)
        rsp = None
        while True:
            try:
                print(edge_ip)
                rsp = requests.post(edge_ip, json=data)
            except:
                while set_flag == 0:
                    pass
                set_flag = 0
            if rsp is not None and rsp.status_code == 200:
                break


def main(id, video_name):
    """
    Main logic of the camera.

    Read video and extract to single frames, for each frame, detect faces in
    the frame, and then encode the face and send it to the edge cache.
    """
    global camera_id, url, v_name

    # url for edge
    camera_id = int(id)
    url = "http://localhost:8080/spring3/getNearestIp/?clientId=%s" % camera_id

    # start zookeeper client to get the newest edge ip
    zk.start()

    face_cascade = "../haarcascade_frontalface_alt.xml"
    cascade = cv2.CascadeClassifier(face_cascade)
    count = 0
    c = 0
    success = True
    multiplier = 10 # change to 2
    v_name = video_name
    video_path = "../videos/%s.avi" % video_name
    vidcap = cv2.VideoCapture(video_path)
    while success:
        frame_id = int(round(vidcap.get(1)))
        success, image = vidcap.read()

        if not success:
            break
        if frame_id % multiplier == 0:
            for i, face in enumerate(cascade.detectMultiScale(image)):
                x, y, w, h = face
                sub_face = image[y:y + h, x:x + w]
                send_img(sub_face, count)
                count += 1

        # send image to server
        c += 1

    print("Finished reading video")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: camera_flask.py <camera_id> <video_name>")
        exit(-1)
    main(sys.argv[1], sys.argv[2])
