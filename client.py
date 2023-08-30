import cv2
import requests

img = cv2.imread('img/Excellent.jpg')

_, img_encoded = cv2.imencode('.jpg', img)

response = requests.get('http://localhost:5000/api/test', data=img_encoded.tobytes())

print(response.json())
