"""API"""
import yaml
from flask import Flask, request

from source.scraper import scrapping
from source.utils import parsedData, rawData, imgFromBytes

app = Flask(__name__)

with open('./config.yaml') as file:
    cfg = yaml.safe_load(file)
    list_path = cfg['URL']['list']
    tuple_path = cfg['URL']['tuple']
    statistic_path = cfg['URL']['statistic']


def updateStatistics(words: iter) -> None:
    """Update statistic in config"""
    with open('./config.yaml') as f:
        config = yaml.safe_load(f)
        config['statistics']['imagesProcessed'] += 1
        config['statistics']['wordsParsed'] += len(words)
    with open('./config.yaml', 'w') as f:
        yaml.dump(config, f, sort_keys=False)


@app.route(list_path)
def listResponse() -> list[str]:
    """Return response as a list of str"""
    limit: int = request.args.get('limit', type=int, default=5)
    answer = scrapping(parsedData(rawData(imgFromBytes(request.data))), limit)
    updateStatistics(answer)
    return answer


@app.route(tuple_path)
def tupleResponse() -> list[tuple[str, str]]:
    """Return response as list of tuples"""
    data: list[str] = parsedData(rawData(imgFromBytes(request.data)))
    limit: int = request.args.get('limit', type=int, default=5)
    scrapped: list[str] = scrapping(data, limit)
    answers: list[tuple[str, str]] = [
        (target, best_matches) for target, best_matches in zip(data, scrapped)
    ]
    updateStatistics(answers)
    return answers


@app.route(statistic_path)
def Statistics() -> dict[str: int]:
    """Return statistics"""
    with open('./config.yaml') as f:
        config = yaml.safe_load(f)

    return {'imagesProcessed': config['statistics']['imagesProcessed'],
            'wordsParsed': config['statistics']['wordsParsed']}


if __name__ == '__main__':
    app.run(port=5000)
