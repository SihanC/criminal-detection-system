"""This file will create experimental data."""
import cv2

# size of the background
b_height = 1800
b_width = 2880


def add_face_criminal(max_h, max_w, frame_num, cid):
    """
    Adding criminal face to the frame.

    This function will add 1 image on the center of the background
    """
    background = cv2.imread("./data/images/background.jpg")
    x_offset = 1400
    y_offset = 800
    face = cv2.imread("./data/images/criminal/%d.png" % (cid))
    if face is None:
        print(cid)
    height, width = face.shape[:2]
    max_height = max_h
    max_width = max_w
    # only shrink if img is bigger than required
    if max_height < height or max_width < width:
        # get scaling factor
        scaling_factor = max_height / float(height)
        if max_width / float(width) < scaling_factor:
            scaling_factor = max_width / float(width)
        # resize image
        face = cv2.resize(
            face, None, fx=scaling_factor, fy=scaling_factor,
            interpolation=cv2.INTER_AREA)

    background[
        y_offset: y_offset + face.shape[0],
        x_offset: x_offset + face.shape[1]] = face

    x_offset += 400 + 200
    cv2.imwrite("./data/output_frames/frame_%d.png" % frame_num, background)


def add_face(max_h, max_w, frame_num, start):
    """
    Adding faces to the frame.

    This function will add 5 images to a white background image.
    """
    background = cv2.imread("./data/images/background.jpg")
    x_offset = 300
    y_offset = 300
    for i in range(start, start + 4):
        face = cv2.imread("./data/images/citizen/c_%d.png" % (i))
        if face is None:
            print(i)
        height, width = face.shape[:2]
        max_height = max_h
        max_width = max_w
        # only shrink if img is bigger than required
        if max_height < height or max_width < width:
            # get scaling factor
            scaling_factor = max_height / float(height)
            if max_width / float(width) < scaling_factor:
                scaling_factor = max_width / float(width)
            # resize image
            face = cv2.resize(
                face, None, fx=scaling_factor, fy=scaling_factor,
                interpolation=cv2.INTER_AREA)

        background[
            y_offset: y_offset + face.shape[0],
            x_offset: x_offset + face.shape[1]] = face

        x_offset += 400 + 200
        if i % 2 != 0:
            y_offset = 1100
        else:
            y_offset = 300

    cv2.imwrite("./data/output_frames/frame_%d.png" % frame_num, background)


def create_video():
    """Creating experimental videos."""
    count = 0
    for i in range(10):
        add_face_criminal(400, 400, count, 18)
        count += 1

    start = 1
    for i in range(11):
        for j in range(10):
            add_face(400, 400, count, start)
            count += 1
        start += 4

    for i in range(10):
        add_face_criminal(400, 400, count, 20)
        count += 1

    for i in range(11):
        for j in range(10):
            add_face(400, 400, count, start)
            count += 1
        start += 4

    for i in range(10):
        add_face_criminal(400, 400, count, 3)
        count += 1

    # define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('./videos/criminals.avi',
                          fourcc, 1, (b_width, b_height))
    for i in range(count):
        try:
            frame = cv2.imread("./data/output_frames/frame_%d.png" % i)
            out.write(frame)
        except:
            break
    out.release()


if __name__ == '__main__':
    create_video()
