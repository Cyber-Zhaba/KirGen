import os
import sys

import cv2
import requests

img = cv2.imread(os.path.join(sys.path[1], 'source', 'imgExamples', 'Excellent.jpg'))

_, img_encoded = cv2.imencode('.jpg', img)

response = requests.get('http://localhost:5000/api/dict',
                        data=img_encoded.tobytes(), params={'limit': 3})

print(response.json())
