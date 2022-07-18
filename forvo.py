#!/bin/python3
# play pronunciation from forvo.com

import sys
import base64
import tempfile
import argparse
import subprocess
from pathlib import Path
import shutil

import fake_useragent
from xdg import BaseDirectory

CACHE_HOME = Path(BaseDirectory.xdg_cache_home) / 'shell-forvo'


class PlayerNotFoundError(Exception):
    pass


def get_mp3_url(word: str, lang: str = '') -> str:
    import bs4
    import requests
    firefox = fake_useragent.UserAgent().ff
    search_page_url = f'https://forvo.com/search/{word}/{lang}'
    soup = bs4.BeautifulSoup(requests.get(search_page_url, headers={
                             'User-Agent': firefox}).text, 'lxml')
    target_tag = soup.select_one('div[id^="play_"]')
    if target_tag is None:
        raise ValueError(f"url for '{word}' in language '{lang}' found")

    onclick_attr = str(target_tag['onclick'])
    _, path_mp3, *_ = onclick_attr.split(';')[0].lstrip('Play(').rstrip(')').split(',')

    # from webpage's javascript:
    # ...
    # path_mp3 = defaultProtocol + '//' + _AUDIO_HTTP_HOST + '/mp3/' + base64_decode(path_mp3);
    # ...

    url_mp3 = f'https://audio00.forvo.com/mp3/{base64.b64decode(path_mp3).decode()}'
    return url_mp3


def fetch_raw_mp3(word: str, lang: str) -> bytes:
    import requests
    firefox = fake_useragent.UserAgent().ff
    url = get_mp3_url(word, lang)
    mp3_content = requests.get(url, headers={'User-Agent': firefox}).content
    return mp3_content


def get_cache_path(word: str, lang: str) -> Path:
    """get the path where mp3 should be cached in filesystem, path's existency is not guaranteed"""
    if lang == '':
        lang = 'default'

    path = CACHE_HOME / f'{word}-{lang}.mp3'
    return path


def cache_exists(word: str, lang: str) -> bool:
    return get_cache_path(word, lang).exists()


def play_sound(mp3_path: str):
    mp3_path = str(mp3_path)
    if (play := shutil.which('play')):
        subprocess.run([play, '-t', 'mp3', mp3_path])
    elif (mpg123 := shutil.which('mpg123')):
        subprocess.run([mpg123, mp3_path])
    elif (ffplay := shutil.which('ffplay')):
        subprocess.run([ffplay, '-autoexit', '-nodisp', mp3_path])
    else:
        raise PlayerNotFoundError(
            "Available audio player not found, install any one of the package ['sox (play)', 'mpg123 (mpg123)', 'ffmpeg (ffplay)'] from your package manager")


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        prog='shell-forvo',
        description="play word's pronunciation from forvo"
    )

    argparser.add_argument('word', action='store')
    argparser.add_argument('-l', '--lang', action='store', help='language codes listed in "https://forvo.com/languages-codes/"', default='')
    argparser.add_argument('--no-cache', '-c', action='store_true', help=f'disable caching the mp3 file to "{CACHE_HOME}/"', default=False)
    args = argparser.parse_args()

    Path.mkdir(CACHE_HOME, exist_ok=True)

    if cache_exists(args.word, args.lang):
        audio_path = get_cache_path(args.word, args.lang)
        print(f'found cached audio `{audio_path}`')
        play_sound(str(audio_path))
        sys.exit(0)

    try:
        mp3_content = fetch_raw_mp3(args.word, args.lang)
    except ValueError as e:
        print(e)
        sys.exit(1)

    if args.no_cache:
        audio_path = Path(tempfile.mkstemp(prefix='python-shell-forvo-', suffix='.mp3'))
    else:
        audio_path = get_cache_path(args.word, args.lang)

    audio_path.write_bytes(mp3_content)
    play_sound(audio_path)
    if args.no_cache:
        audio_path.unlink()
