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
from telebot import types
import time

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

with open("keys.json", "r") as file:
    keys = json.loads(file.read());

bot = telebot.TeleBot(keys['telegram_key'])

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of spreadsheet
SPREADSHEET_ID = keys['spreadsheet_id']
SHEET_NAME = keys['sheet_name']

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

@bot.message_handler(commands=['start','help])
def send_welcome(message):
    bot.reply_to(message,'Welcome Use /lol to send your location :). Check out /test_drive too')

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message,'To help')


@bot.message_handler(commands=['lol'])
def send_allstuff(message):
    markup = types.ReplyKeyboardMarkup()#one_time_keyboard=True)
    itembtn2 = types.KeyboardButton('contact',request_contact=True)
    itembtn3 = types.KeyboardButton('location',request_location=True)
    markup.add(itembtn2, itembtn3)

    msg = bot.reply_to(message,"Try sending location",reply_markup=markup)
    bot.register_next_step_handler(msg,loc_cont_handling)

def loc_cont_handling(message):
    try:
        chat_id = message.chat.id
        if (message.location):
            print(message.location)
            bot.reply_to(message,'Nice got your location')

        if (message.contact):
            print(message.contact)
            bot.reply_to(message,'Nice got your contact')

        markup = None
    except:
        bot.reply_to(message,'sad chec')

# testing google drive integration
@bot.message_handler(commands=['test_drive'])
def google_drive_test(message):
    values_list = gsheet.row_values(1)
    bot.reply_to(message, "Works" + ', ' . join(values_list))

#if __name__ == "__main__":
bot.polling()
app.run(host='0.0.0.0', port=8080, debug=True)
