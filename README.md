## Introduction
a python3 script to play audio from forvo.com in shell for language learning or whatever other usage.

## Preparation
1. Install required python libraries: `pip install -r requirements.txt`
2. Install one of the three package: `sox`, `mpg123`, `ffmpeg` from your package repository as the script will choose one and call a subprocess of them for audio playing.

## Example
`python shell_forvo.py "hello"` # forvo default

`python shell_forvo.py "яйцо" --lang ru` # Russian

`python shell_forvo.py "яйцо" --lang be` # Belarusian

`python shell_forvo.py "鬼" --lang zh` # Mandarin Chinese

`python shell_forvo.py "鬼" --lang ja` # Japanese

`python shell_forvo.py "pornography" --no-cache` # Do not cache the audio in filesystem

## Install
No installation method yet but you can always do something like `mv shell_forvo.py "$HOME/.local/bin/sfv"` for simple run.
