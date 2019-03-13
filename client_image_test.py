import requests
import cv2

addr = 'http://localhost:5000'
test_url = addr + '/process'

# prepare headers for http request
content_type = 'image/jpeg'
headers = {'content-type': content_type}

img = cv2.imread('test_images/person1.jpg')
# encode image as jpeg
_, img_encoded = cv2.imencode('.jpg', img)
# send http request with image and receive response
response = requests.post(
    test_url, data=img_encoded.tostring(), headers=headers)
# print response
print response.text
