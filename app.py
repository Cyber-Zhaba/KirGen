from flask import Flask, request

from utils import parsedData, rawData, imgFromBytes
from scraper import scrapping

app = Flask(__name__)


@app.route('/api/test')
def index():
    return scrapping(parsedData(rawData(imgFromBytes(request.data))))


if __name__ == '__main__':
    app.run(port=5000)
