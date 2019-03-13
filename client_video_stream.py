import numpy as np
import cv2
import time
import requests

addr = 'http://localhost:5000'
url = addr + '/process'

content_type = 'image/jpeg'
headers = {'content-type': content_type}

# cap = cv2.VideoCapture('test_videos/Li165C-DN.mp4')
cap = cv2.VideoCapture(0)

frame_rate = 5
prev = 0

while(cap.isOpened()):

    time_elapsed = time.time() - prev
    res, image = cap.read()

    if time_elapsed > 1./frame_rate:
        prev = time.time()

        # TODO send request and wait for response in another thread

        _, img_encoded = cv2.imencode('.jpg', image)
        response = requests.post(
            url, data=img_encoded.tostring(), headers=headers)

        cv2.imshow('frame', image)

        print prev
        print response.text
        print

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
