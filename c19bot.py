#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
import flask
import random
import logging
import telebot
import requests
import urllib.request
import requests_cache
from flask import Flask
from flask import request
from flask import render_template

req = requests.Session()
requests_cache.install_cache('genlib_cache')

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
app.debug = False
app.config['PROPAGATE_EXCEPTIONS'] = True

logging.basicConfig(filename='error.log', level=logging.DEBUG)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'}

bot = telebot.TeleBot("1753956236:AAEHU-z2sHjqvrO4CENxmCk99kHgGbaC-pQ")

@app.route('/', methods=['GET'])
def hello_world():
	return 'Hello, World!1'


@app.route('/', methods=['POST', 'PUT'])
def receiveMessage():
	if request.method == "POST" and flask.request.headers.get('content-type') == 'application/json':
		json_string = request.get_json()
		update = telebot.types.Update.de_json(json_string)
		bot.process_new_messages([update.message])
		return flask.Response(response={}, content_type='application/json')
	else:
		return flask.Response(response=None, content_type='application/json')

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "How can I help you today? send /search to start")
