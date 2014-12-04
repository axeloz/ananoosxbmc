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
import xbmcgui
import urllib
import urllib2
import json
import cookielib
from cookielib import CookieJar, DefaultCookiePolicy
import resources.lib.Utils as Utils
import tempfile

default = sys.modules['__main__']

class Api():

	def __init__(self):
		self.allowed_domains    = ["ananoos.com", ".ananoos.com"]
		self.api_url            = sys.modules['__main__'].API_URL
		self.cookiejar_dir      = default.addon.getSetting('cookiejar')
		self.cookies            = {}

		if not os.path.isdir(self.cookiejar_dir):
			self.cookiejar_dir = tempfile.mkdtemp()
			Utils.log('Creating a new Cookiejar in '+self.cookiejar_dir)
			default.addon.setSetting('cookiejar', self.cookiejar_dir)

		self.cookiejar		= self.cookiejar_dir+'/cookies.lwp'	
		Utils.log('Using cookiejar: '+self.cookiejar)

	def Browse(self, parent = "0"):
		return self.__Call(url='BrowseFiles', params={'parent': parent})

	def getStreamUrl(self, item_id = None):
		if item_id is None:
			return False

		return self.__Call(url='StreamFile', params={'file': item_id})

	def Login(self, username = None, password = None):
		if username is None or password is None:
			return False

		return self.__Call(url='Auth', params={'username': username, 'password': password})

	def getCookies(self):
		return self.cookies	

	def Logout(self):
		return self.__Call(url='Logout')

	def __Call(self, url, params = {}):

		#xbmc.executebuiltin('Notification('+default.language(30015)+', '+language(30016)+',3000,' + default.addon_path +'/resources/images/success.png)')

		# Matching URL
		if not re.search('http(s)?://', url):
			url = self.api_url + '/' + url

		Utils.log('Requesting URL : '+url+'?'+urllib.urlencode(params))

		# Running request
		try:
			# Setting cookies default policy
			policy = DefaultCookiePolicy(rfc2965=False, allowed_domains=self.allowed_domains)
			cj = cookielib.LWPCookieJar(policy=policy)

		 	# Starting the CookieJar handler
		 	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj)) 
		 	urllib2.install_opener(opener)

			# Starting the request
			req = urllib2.Request(url)
			req.add_header('User-Agent', Utils.getUserAgent())

			# Loading existing cookie(s) if applicable
			# Ignoring_discard  = True otherwise session cookies aren't sent
			if os.path.isfile(self.cookiejar):
				Utils.log('Loading existing cookies')
				cj.load(self.cookiejar, ignore_discard=True)

			# Running query
			response = urllib2.urlopen(req, urllib.urlencode(params))
			# Getting response
			content     = response.read()
			# Getting response informations
			infos    = response.info()

			# Checking the response content-type
			if infos['content-type']:
				# If response is a JSON, decoding JSON automatically
				if re.search('application/json', infos['content-type']):
					content = json.loads(content)

			# Saving private_key for later use
			for cookie in cj:
				self.cookies[cookie.name] = cookie.value

			# If unable to save the cookie jar file
			# Aborting execution, otherwise going into
			# An infinite loop
			if not os.path.isdir(self.cookiejar_dir):
		
				Utils.log('Warning: Cookiejar DIR does not exist') 
				xbmcgui.Dialog().ok(default.language(30023), '', default.language(30024))
				sys.exit()

			# Saving any cookie sent with the response
			# Ignoring_discard  = True otherwise session cookies aren't saved				
			cj.save(self.cookiejar, ignore_discard=True)    

			response.close()
			return content


		except urllib2.HTTPError, e:
			# Authentication issue, resetting the private key
			if e.code == 403:
				Utils.log('Got a 403 Forbidden, trying to login now')
				if default.Auth.Login():
					default.browse()

			#Utils.log('API Call error: ' + str(e))
			#xbmc.executebuiltin('Notification(An error occurred, Something nasty happened. Sorry...,3000,' + default.addon_path + '/resources/images/error.png)')

		except urllib2.URLError, e:
			Utils.log('Could not request the API (' + str(e) + ')')
			xbmc.executebuiltin('Notification(An error occurred, Something nasty happened. Sorry...,3000,' + default.addon_path + '/resources/images/error.png)')

		except:
			Utils.log('Something nasty happened during API Call (' + str(sys.exc_info()[0]) + ')')
			xbmc.executebuiltin('Notification(An error occurred, Something nasty happened. Sorry...,3000,' + default.addon_path + '/resources/images/error.png)')
			return False
