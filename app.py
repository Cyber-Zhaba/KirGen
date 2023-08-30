from flask import Flask, request

from utils import parsedData, rawData, imgFromBytes

app = Flask(__name__)


@app.route('/api/test')
def index():
    return parsedData(rawData(imgFromBytes(request.data)))


if __name__ == '__main__':
    app.run(port=5000)
