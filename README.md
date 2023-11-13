# t-bot

Upload files to your Telegram channel or group with your telegram bot

 [![PyPI version](https://badge.fury.io/py/tl-bot.svg)](https://pypi.org/project/tl-bot/)
 [![Downloads](https://pepy.tech/badge/tl-bot/month)](https://pepy.tech/project/tl-bot)
 [![Downloads](https://static.pepy.tech/personalized-badge/tl-bot?period=total&units=international_system&left_color=green&right_color=blue&left_text=Total%20Downloads)](https://pepy.tech/project/tl-bot)
 ![GitHub Contributors](https://img.shields.io/github/contributors/jakbin/t-bot)
 ![GitHub commit activity](https://img.shields.io/github/commit-activity/m/jakbin/t-bot)
 ![GitHub last commit](https://img.shields.io/github/last-commit/jakbin/t-bot)
 ![Python 3.6](https://img.shields.io/badge/python-3.6-yellow.svg)


## Features
- Progress bar
- You can change file name before upload on telegram

Note : Bot can upload only 50 MB file (with default telegram bot api server url)


## Installation

```sh
pip3 install tl-bot
```

## Usage 
```sh
t-bot setup               # setup your telegram credentials
t-bot reset               # reset to default your telegram credentials
t-bot test                # test telegram bot token
t-bot getid               # get chat id of your connected group or channel
t-bot up {file_name} -c file_caption       # upload Telegram channel or group
t-bot d {url} -c caption                   # download and upload file to your Telegram channel or group
```

# API

The anonfile-upload client is also usable through an API (for test integration, automation, etc)

### tl_bot.main.test_token(bot_token)

```py
from tl_bot.main import test_token

test_token(bot_token)   # bot_token type str
```

### tl_bot.main.uploader(bot_token: str, chat_id: str, file_name: str, server_url: str, caption: str)

```py
from tl_bot.main import uploader

uploader(bot_token, chat_id, file_name, server_url, caption)    # all arguments must be str
```

### tl_bot.main.download(url:str, bot_token:str, chat_id:str, caption:str)

```py
from tl_bot.main import download

download(url, bot_token, chat_id, caption)    # all arguments must be str
```