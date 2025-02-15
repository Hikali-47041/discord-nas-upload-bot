# discord-nas-upload-bot
Discordのチャンネルに投稿されたAttachmentsをNASにアップロードするボット(開発終了)

## install(Using Docker)
1. clone this repository && cd to repository directory
2. setup tokens  
    - move `sample.env` to `.env`
    - edit `.env` file
3. `docker compose up -d`

## install(Directroy)
1. install [python3](https://www.python.org/) and `python3-pip`
2. clone this repository && cd to repository directory
3. (Optional)(Recommended) setup venv  
`python -m venv venv`  
`source venv/bin/activate`
4. install packages  
`pip install -r requirements.txt`
5. setup tokens  
    - move `sample.env` to `.env`
    - edit `.env` file
6. run  
`python discord_bot.py`
