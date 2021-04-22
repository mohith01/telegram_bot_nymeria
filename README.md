# Telegram bot for Volunteers

This bot is to provide support to the volunteers working in 🆘Query Tracker & Resolution

## Installation

- Create a new API key using [@botfather](https://t.me/BotFather)
- Create or clone the Google Sheet to be used for backend
- Create new `credentials.json` for Sheets API using [Google Cloud Console](https://console.cloud.google.com)
- Share the Google Sheet with user in `credentials.json`
- Clone the Repo and install `requirements.txt`
- Run `c19bot.py`; or set `FLASK_APP` and do `flask run`

## Usage
```
/start - initiates the conversation and prints commands available
/addResource - Provides interface to add resources.
/searchResource - Helps you search resources from the Sheet linked.
/verify - Lets you change the status and verification status of a resource
```
## Contributing
Discuss in the telegram group. If you have a concern/suggestion/feedback, please open an issue.
