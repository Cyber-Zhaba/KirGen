"""Scrapping"""
import asyncio
import http
import urllib.parse
from asyncio import Task
from enum import Enum
from pprint import pprint

import aiohttp
from bs4 import BeautifulSoup as BS
from bs4.element import Tag
from fuzzywuzzy import process

from utils import parsedData, rawData, imgFromFile


class Dict(Enum):
    """
    Dictionaries from gramota.ru in which the word will be searched
    :arg SP:  Орфографический словарь
    :arg LED: Большой толковый словарь
    :arg RVS: Русское словесное ударение
    :arg DPN: Словарь имён собственных
    :arg DS:  Словарь синонимов
    :arg SQF: Синонимы: краткий справочник
    :arg DOA: Словарь антонимов
    :arg DMT: Словарь методических терминов
    :arg DRN: Словарь русских имён
    """
    SP = {'lop': 'x'}
    LED = {'bts': 'x'}
    RVS = {'zar': 'x'}
    DPN = {'ag': 'x'}
    DS = {'ab': 'x'}
    SQF = {'sin': 'x'}
    DOA = {'lv': 'x'}
    DMT = {'az': 'x'}
    DRN = {'pe': 'x'}


garbage_words = 'звездочка * вопросительный знак ? Звездочка * Вопросительный знак ? ' \
                'чес*ный,  проф*ес*ор,  ветрен*ый. фа фа-бекар фа-бемоль фа-бемольный'  # noqa


def scrapping(parsedWords: list[str], limit: int = 5, *args: Dict) -> list[str]:
    """
    Launching scraping on the gramota.ru using the specified dictionaries.
    :param parsedWords:
    :param limit: number of matches for one word
    :param args: the dictionaries used . By default, SP, RVS, DPN, DRN
    :return: a list with the best matches for each word.
    The quality of the match is determined using the Levenshtein distance
    """
    dicts = form_dicts(args)
    scrapping_result: list[list[str]] = asyncio.run(async_scraping(parsedWords, dicts))
    scrapping_processed: list[str] = []

    for word, matches in zip(parsedWords, scrapping_result):
        processed: list[tuple[str, int]] = process.extract(word, matches, limit=limit)
        generator = map(lambda x: x[0], processed)

        scrapping_processed.append(" | ".join(generator))

    return scrapping_processed


async def async_scraping(parsedWords: list[str], dicts: dict[str, str]) -> list[list[str]]:
    """
    Starts async word parsing
    :param parsedWords:
    :param dicts:
    :return: a list of lists
    where the index of each word
    from the original list corresponds to a
    set of words found on the page
    """
    async with aiohttp.ClientSession() as session:
        tasks: list[Task] = []
        for word in parsedWords:
            task: Task = asyncio.create_task(gramota(session, word, dicts))
            tasks.append(task)
        res: list[list[str]] = await asyncio.gather(*tasks)
    return res


async def gramota(
        session: aiohttp.client.ClientSession,
        word: str,
        params: dict[str, str]
) -> list[str]:
    """
    Async parsing of a web page to find the correct spelling of a word.
    If the word is not found, then the ending of the word is cut off, and
    it gets additional characters at the beginning and end
    :param session: aiohttp session
    :param word:
    :param params: dict of using Dicts
    :return: all found words and phrases.
    The capital letter highlights the correct stress in the word.
    The list needs post-processing because there is a lot of garbage on the page
    """
    params['word'] = word
    url = 'http://www.gramota.ru/slovari/dic/?' + urllib.parse.urlencode(params)
    async with session.get(url) as resp:
        scrapped_words: list[str] = []
        if resp.status == http.HTTPStatus.OK.value:
            resp_content: str = await resp.text()
            soup = BS(resp_content, 'html.parser')
            main_div: Tag = soup.find('div', attrs={'class': 'inside block-content'})
            for b in main_div.find_all('b'):
                if b.text not in garbage_words:
                    if b.find('span', attrs={'class': 'accent'}):
                        span: list[str] = str(b)[3:-4].split('<span class="accent">')
                        for i, _ in enumerate(span):
                            span[i] = span[i].lower()
                            span[i] = span[i].replace('<span class="em1">', '')
                            span[i] = span[i].replace('</span>', '')
                            if i != 0:
                                span[i] = span[i][0].upper() + span[i][1:]
                        scrapped_words.append(''.join(span))
                    else:
                        scrapped_words.append(b.text.lower())

            if not scrapped_words and (word[0] != '*' or word[-1] != '*'):
                new_word = '*' + word[:-2] + '*'
                scrapped_words: list[str] = await gramota(session, new_word, params)

        return scrapped_words


def form_dicts(dict_list: tuple[Dict]) -> dict[str, str]:
    """
    Get dictionaries that are used in parsing
    :param dict_list:
    :return:
    """
    dicts = {}
    if dict_list:
        for arg in dict_list:
            dicts |= arg.value
    else:
        # Default
        dicts = Dict.SP.value | Dict.RVS.value | \
                Dict.DPN.value | Dict.DRN.value

    return dicts


if __name__ == '__main__':
    data = parsedData(rawData(imgFromFile('Excellent.jpg')))

    for target, best_matches in zip(data, scrapping(data)):
        pprint(f"{target}: {best_matches}")
