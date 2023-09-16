"""Image processing and Target Words detection"""
import os
import sys
from pprint import pprint
from typing import TypeAlias, Literal

import cv2
import numpy as np
import pytesseract

Image: TypeAlias = np.ndarray
File: TypeAlias = Literal[
    "Excellent.jpg", "Good.jpg", "Normal.jpg", "Bad.jpg", "Terrible.jpg"
]

SpecSymbols: list[str] = ['.', '(', ')', '_']
Punctuation: list[str] = [',', '!', ' ', '?', ':', ';']


def imgFromFile(filename: File) -> Image:
    """Read Pre-build images in imgExamples directory

    :param str filename: Name of file in imgExamples directory
    :return: Image.
    """
    img = cv2.imread(os.path.join(sys.path[0], 'imgExamples', filename))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


def imgFromBytes(byte_list: bytes) -> Image:
    """Get Image from bytes

    :param bytes byte_list:
    :return: Image.
    """
    # noinspection PyTypeChecker
    array: np.ndarray = np.fromstring(byte_list, np.uint8)
    img: Image = cv2.imdecode(array, cv2.COLOR_BGR2RGB)
    return img


def rawData(img: Image) -> str:
    """Extract text from Image via TesseractORC"""
    return pytesseract.image_to_string(img, lang='rus')


def parsedData(raw: str) -> list[str]:
    """Get target words from string that contains all detected words

    :param raw: all words detected on Image
    :return: List of target words.
    """

    def findTarget(word: str) -> bool:
        return set(SpecSymbols) & set(word) != set()

    def filterTargets(word: str) -> bool:
        if len(word) <= 1:
            return False
        return True

    raw_list: list[str] = raw.split()

    targets: iter = filter(findTarget, raw_list)
    targets = map(proceed, targets)

    targets_filtered: iter = filter(filterTargets, targets)

    return list(targets_filtered)


def proceed(word: str) -> str:
    """Proceed word

    :param word:
    :return: proceeded word.

    Examples
    --------
    >>> proceed('Нефт...пр...вод.')
    'нефт*пр*вод*'
    >>> proceed('миро(воз, вос)зрение,')
    'миро*зрение'
    >>> proceed('само(во$, вос)г@раNие')
    'само*г*ра*ие'
    >>> proceed('...бежать')
    '*бежать'
    >>> proceed('(с, з)горать')
    '*горать'
    """

    def cyclic_only(letter: str) -> str:
        if ord('а') <= ord(letter) <= ord('я') \
                or letter in SpecSymbols \
                or letter == 'ё':
            return letter
        if letter in Punctuation:
            return ''
        return '*'

    word = word.lower()
    word = ''.join(map(cyclic_only, iter(word)))

    if '(' in word and ')' in word:
        word = word[:word.find('(')] + "*" + word[word.rfind(')') + 1:]

    for spec in SpecSymbols:
        word = word.replace(spec, '*')

    surrounded_word = '~' + word + '~'

    word_filtered: iter = filter(bool, surrounded_word.split('*'))

    return "*".join(word_filtered)[1:-1]


if __name__ == '__main__':
    pprint(rawData(imgFromFile('Excellent.jpg')))

    pprint(parsedData(rawData(
        imgFromFile('Excellent.jpg')
    )))
