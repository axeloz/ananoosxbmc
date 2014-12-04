#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
   Ananoos plugin for XBMC
   Copyright (C) 2014 Axel de Vignon
   License: Apache 2.0 (See license.txt)
'''


import os
import re
import sys
import xbmc
import urllib
import urllib2
import json
import cookielib
from cookielib import CookieJar, DefaultCookiePolicy

default = sys.modules['__main__']

def getUserAgent():
	return default.plugin + ' (XBMC/' + default.xbmc_version + ', BuildDate: ' + default.xbmc_date + ')'


def encode(string):
	try:
		return string.encode('utf-8','replace')
	except:
		log('ENCODE() - Failed to encode to UTF-8')

	try:
		return string.encode('latin','replace')
	except:
		log('ENCODE() - Failed to encode to latin')

	try:
		return string.decode(ENCODING,'replace').encode('utf-8','replace')
	except:
		log('ENCODE() - Failed to encode to UTF-8 (alt-method) - using repr()')
		ret = repr(string)
		if ret.startswith('u'): ret = ret[1:]
		return ret[1:-1]


def error(message):
	log(message)
	return str(sys.exc_info()[1])

def log(message):
	# Hidding password into the logs
	message = re.sub('password=[a-zA-Z0-9_-]+', 'password=[hidden]', message)

	print default.plugin + ': %s' % encode(str(message))
	xbmc.log("%s: %s" % (default.plugin,
                         message),
                         level=xbmc.LOGDEBUG)



# Generating Auth Dialog
from resources.lib.pyxbmct.addonwindow import *
class AuthForm(AddonDialogWindow):

	def __init__(self, title=''):
		# You need to call base class' constructor.
		super(AuthForm, self).__init__(title)
		# Set the window width, height and the grid resolution: 2 rows, 3 columns.
		self.setGeometry(600, 350, 7, 3)

		self.__setControls()
		self.__setNavigation()

	def __setControls(self):
		# introduction message
		text1 = Label(default.language(30007))
		self.placeControl(text1, 0, 0, columnspan=3)
		text2 = Label(default.language(30008))
		self.placeControl(text2, 1, 0, columnspan=3)
		text3 = Label(default.language(30009))
		self.placeControl(text3, 2, 0, columnspan=3)

		# form
		label1 = Label(default.language(30012))
		self.placeControl(label1, 4, 0)
		self.username = Edit('username')
		self.placeControl(self.username, 4, 1, columnspan=2)
		label2 = Label(default.language(30002))
		self.placeControl(label2, 5, 0)
		self.password = Edit('password', isPassword=1)
		self.placeControl(self.password, 5, 1, columnspan=2)

		self.username.setText(default.addon.getSetting('username'))
		self.password.setText(default.addon.getSetting('password'))


		# Create a button.
		self.button = Button(default.language(30010))
		# Place the button on the window grid.
		self.placeControl(self.button, 6, 1)
		# Set initial focus on the button.
		self.setFocus(self.username)
		# Connect the button to a function.
		self.connect(self.button, lambda:self.doLogin())
		# Connect a key action to a function.
		self.connect(ACTION_NAV_BACK, self.close())

	def __setNavigation(self):
		"""Set up keyboard/remote navigation between controls."""
		self.username.controlUp(self.button)
		self.username.controlDown(self.password)
		self.password.controlUp(self.username)
		self.password.controlDown(self.button)
		self.button.controlUp(self.password)
		self.button.controlDown(self.username)

	def doLogin(self):
		if len(self.username.getText()) > 0 and len(self.password.getText()) > 0:
			default.Auth.Login(username = self.username.getText(), password = self.password.getText())
		else:
			return

	def doClose(self):
		self.close()


