# svrusoundbot
Telegram bot for the voice of the Swedish-Russian dictionary from the docx table


Made at the request of a man named Stark.

Available here: [@svrusoundbot](https://t.me/svrusoundbot).

## How to deploy on your server?

There are already compiled executable independent files for [Windows x86](https://github.com/alekssamos/svrusoundbot/releases/download/v1.2/svrusoundbot.exe) and [Linux x64](https://github.com/alekssamos/svrusoundbot/releases/download/v1.2/svrusoundbot).

If the file does not run on some Linux systems, do this before starting:
```bash
export TMPDIR=./tmp; mkdir -p  $TMPDIR
```


Otherwise
Python must be installed on your system.

Tested on Python versions 3.8 - 3.11


Launch via docker is also available

### Get the bot source 
#### from github:
```bash
git clone https://github.com/alekssamos/svrusoundbot
cd svrusoundbot

```

create a python virtual environment

```bash
python -m venv venv
# or
python3 -m venv venv
```

install dependencies

on windows:
```bat
venv\Scripts\python -m pip install -r requirements.txt
```

on linux:

```bash
venv/bin/python -m pip install -r requirements.txt
```
#### or from docker container:
```bash
docker pull ghcr.io/alekssamos/svrusoundbot:v1.2
```
### Configuration
* Get bot token from https://t.me/BotFather
* Get your own Telegram API key from https://my.telegram.org/apps
* rename `.env.example` to `.env` and edit by filling in the values
### Launch it
#### Directly
on windows:
```bat
venv\Scripts\python svrusoundbot.py
```
on linux:

```bash
venv/bin/python svrusoundbot.py
```
#### through docker
```bash
docker run --env-file .env ghcr.io/alekssamos/svrusoundbot:v1.2
```

Everything is ready!
