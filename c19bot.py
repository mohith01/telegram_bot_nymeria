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
	bot.reply_to(message, "How can I help you today? send /search <bookname> to search for a book")

# Handle '/search'
@bot.message_handler(commands=['search'])
def sendBooks(message):
	cid = message.chat.id
	bot.send_chat_action(cid, 'typing')
	userName = message.from_user.first_name
	queryText = message.text
	if '/search' in queryText:
		queryText = queryText.replace('/search','')
	queryText = queryText.strip().lower()

	ebook_format = 'epub'
	if ' format:' in queryText:
		ebook_format = queryText.split(' format:', 1)[1]
		queryText = queryText.split(' format:', 1)[0]

	logging.debug('Query : ' + queryText)
	logging.debug('Format : ' + ebook_format)

	if len(queryText) == 0:
		sentMsg = bot.reply_to(message, 'Hello '+userName+', tell me the title of the book you are looking for. /search <book name>')
		return;
	
	if '@irmap' in queryText:
		sentMsg = bot.reply_to(message, 'Yes, I shall help you. Tell me the title of the book you are looking for. /search <book name>')
		return;
	
	if len(queryText) < 5:
		sentMsg = bot.reply_to(message, 'Hello '+userName+', there are far too many books in this library, can you be more specific?')
		return;
	
	searchUrl = "http://gen.lib.rus.ec/fiction/?q="+queryText+"&language=English&format=" + ebook_format
	searchReq = req.get(url=searchUrl, headers=headers).text

	if 'No files were found.' in searchReq:
		if random.choice([True, False]):
			bot.reply_to(message, "Oh hmm.. I couldn't find it anywhere. Perhaps it is time to look at the dues register.")
		else:
			bot.reply_to(message, "Aaaa.. nope. No such book here Let me check the dues register.")

		# check non-fiction
		searchUrl = "http://gen.lib.rus.ec/search.php?req="+queryText+"&lg_topic=libgen&open=0&view=simple&res=25&phrase=1&column=def"
		searchReq = req.get(url=searchUrl, headers=headers).text

		if '0 files found' in searchReq:
			if random.choice([True, False]):
				bot.reply_to(message, "Sorry love, couldn't find it.")
			else:
				bot.reply_to(message, "Nope, sorry. Couldn't find it.")
			return;
		if random.choice([True, False]):
			bot.reply_to(message, 'Oh look, I found a copy in the return pile. Fetching one for you.')
		else:
			if random.choice([True, False]):
				bot.reply_to(message, "Found a copy in the returns pile! Here you go.")
			else:
				if random.choice([True, False]):
					bot.reply_to(message, "Here you go, snatched this one from a defaulters hands.")
				else: 
					bot.reply_to(message, "Here, pardon the blood stains. Dealing with defaulters can get a bit.. messy.")

		dLink = 'http' + searchReq.split('[1]', 1)[0].rsplit('http',1)[1].split("'",1)[0]
		logging.debug('dLink : ' + dLink)
		dPage = req.get(dLink, headers=headers).text
		dLink = 'http://' + dPage.split('h2',1)[1].split('http://',1)[1].split('"',1)[0]
		dDomain = dLink.split('/')[2]
		cLink = 'http://' + dDomain + dPage.split('<img',1)[1].split('src="',1)[1].split('"',1)[0]
		filename = cLink.split('/')[-1]
		urllib.request.urlretrieve(cLink, 'tmp/'+filename)
		coverImage = open('tmp/'+filename, 'rb')

		title = dPage.split('<h1>',1)[1].split('</h1>',1)[0]
		author = dPage.split('Author(s): ',1)[1].split('</p',1)[0]
		caption = "Title: <b>" + title + '</b>\nAuthor: ' + author + '\n<a href="' + dLink + '">Download File</a>'
		bot.send_photo(cid, coverImage, caption=caption, parse_mode='HTML')
		os.remove('tmp/'+filename)

	else:
		count = searchReq.split('catalog_paginator',1)[1].split('<div',1)[1].split('>',1)[1].split(' ',1)[0]
		count = int(count)
		textmsg = 'I found ' + str(count) + ' copy. Here you go!'
		if count > 1:
			textmsg = 'I found ' + str(count) + ' copies. Here you go!'
		if count > 10:
			textmsg = 'Oh look, I found ' + str(count) + ' copies. Fetching one for you.'
		if count > 40:
			textmsg = 'Would you look at that, I found ' + str(count) + ' copies. Let me fetch you one of these.'
		if count > 100:
			textmsg = 'This seems like a popular book, I found ' + str(count) + ' copies. Fetching one for you.'
		bot.reply_to(message, textmsg)
		
		dLink = 'http' + searchReq.split('record_mirrors_compact', 1)[1].split('http',1)[1].split('"',1)[0]
		dPage = req.get(dLink, headers=headers).text
		dLink = 'http://' + dPage.split('h2',1)[1].split('http://',1)[1].split('"',1)[0]
		dDomain = dLink.split('/')[2]
		cLink = 'http://' + dDomain + dPage.split('<img',1)[1].split('src="',1)[1].split('"',1)[0]
		filename = cLink.split('/')[-1]
		urllib.request.urlretrieve(cLink, 'tmp/'+filename)
		coverImage = open('tmp/'+filename, 'rb')

		title = dPage.split('<h1>',1)[1].split('</h1>',1)[0]
		author = dPage.split('Author(s): ',1)[1].split('</p',1)[0]
		caption = "Title: <b>" + title + '</b>\nAuthor: ' + author + '\n<a href="' + dLink + '">Download '+ebook_format+' File</a>'
		bot.send_photo(cid, coverImage, caption=caption, parse_mode='HTML')
		os.remove('tmp/'+filename)

