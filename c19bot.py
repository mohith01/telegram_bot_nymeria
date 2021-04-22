#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Some of the imports are useless, keeping for now
import re
import json
import flask
import random
import logging
import os.path
import telebot
import gspread
import requests
import urllib.request
import requests_cache
from flask import Flask
from flask import request
from flask import render_template
from oauth2client.service_account import ServiceAccountCredentials

# Speeds up requests sometimes, can also cause issues so delete nymeria_cache.sql when needed
req = requests.Session()
requests_cache.install_cache('nymeria_cache')

app = Flask(__name__)

# Bunch of stuff to make debugging easier, disable debug during production
app.logger.setLevel(logging.INFO)
app.debug = True
app.config['PROPAGATE_EXCEPTIONS'] = True
logging.basicConfig(filename='error.log', level=logging.DEBUG)

# Another thing for requests in future
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'}

bot = telebot.TeleBot("1753956236:AAEHU-z2sHjqvrO4CENxmCk99kHgGbaC-pQ")

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of spreadsheet
SPREADSHEET_ID = '1f2ISwsayDXGMy09gVbRwn1Xed2OL7F9WsIxYlyLAWC4'
SHEET_NAME = 'Telegram Bot'

# Creating the credentials is a process on its own off script.
credential = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPES)
client = gspread.authorize(credential)
gsheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)


# This is just so we can visit the url and confirm if the script is working at a glance
# This can be built into a whole website later if needed
@app.route('/', methods=['GET'])
def hello_world():
	return 'Hello, World!1'

# This handles all the request received via Telegram
@app.route('/', methods=['POST', 'PUT'])
def receiveMessage():
	if request.method == "POST" and flask.request.headers.get('content-type') == 'application/json':
		json_string = request.get_json()
		update = telebot.types.Update.de_json(json_string)
		bot.process_new_messages([update.message])
		return flask.Response(response={}, content_type='application/json')
	else:
		return flask.Response(response=None, content_type='application/json')

## Start of actual code, we specify commands and then a function which handles the commands.

# start/help - to give intro to all the commands or other stuff
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "How can I help you today? send /search to start")

# testing google drive integration
@bot.message_handler(commands=['test_drive'])
def google_drive_test(message):
    values_list = gsheet.row_values(1)
    bot.reply_to(message, "Works" + ', ' . join(values_list))