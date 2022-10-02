# svrusoundbot
Telegram bot for the voice of the Swedish-Russian dictionary from the docx table


Made at the request of a man named Stark.

Available here: [@svrusoundbot](https://t.me/svrusoundbot).

## How to deploy on your server?

Python must be installed on your system.
Tested on Python versions 3.8 - 3.11

### Get the bot
#### from github:
```bash
git clone https://github.com/alekssamos/svrusoundbot
cd svrusoundbot
# create python virtual enviroment
python -m venv venv
# or
python3 -m venv venv
# install dependencies
# on windows:
venv\Scripts\python -m pip install -r requirements.txt
# on linux:
venv/bin/python -m pip install -r requirements.txt
```
#### org from docker container:
```bash
docker pull ghcr.io/alekssamos/svrusoundbot:latest
```
### Configuration
* Get bot token from https://t.me/BotFather
* Get your own Telegram API key from https://my.telegram.org/apps
* rename `.env.example` to `.env` and edit by filling in the values
### Launch it
#### Directly
```bash
# on windows:
venv\Scripts\python svrusoundbot.py
# on linux:
venv/bin/python svrusoundbot.py
```
#### through docker
`docker run ghcr.io/alekssamos/svrusoundbot:latest --env-file .env`
Everything is ready!
