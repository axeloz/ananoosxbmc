#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
   Ananoos plugin for XBMC
   Copyright (C) 2014 Axel de Vignon
   License: Apache 2.0 (See license.txt)
'''


import sys
import xbmc, xbmcgui
import resources.lib.Utils as Utils


default = sys.modules['__main__']

# Handling Auth
class Auth():

	def __init__(self):
		self.addon 			= default.addon
		self.username		= self.addon.getSetting('username') or ''
		self.password		= self.addon.getSetting('password') or ''
		self.window			= ''

	def Login(self, username = None, password = None):

		Utils.log('Checking login now')
		modal = 0

		# Checking whether arguments were sent
		if username is not None:
			self.username = username

		if password is not None:
			self.password = password

		# If username OR password are NOT available, opening modal box
		if self.username is None or self.password is None:
			Utils.log('Never logged in before, displaying modal')
			self.window = Utils.AuthForm(default.language(30006))
			self.window.doModal()
			return

		try:
			content = default.Api.Login(username=self.username, password=self.password)
			if not content or content == False:
					return False

			if content['result'] and content['result'] == 'success':
				#xbmc.executebuiltin('Notification('+default.language(30015)+', '+language(30016)+',3000,' + default.addon_path +'/resources/images/success.png)')
				Utils.log('Login is successful.')

				# If modal is opened, closing it
				if self.window:
					Utils.log('Trying to close login modal')
					self.window.close()

				# Saving username and password into the XBMC settings
				self.addon.setSetting('username', str(self.username))
				self.addon.setSetting('password', str(self.password))

				return True
			else:
				Utils.log('Login failed')
				xbmcgui.Dialog().ok(default.language(30015), '', default.language(30017), default.language(30018))

				if not self.window:
					self.window = AuthForm(default.language(30006))
					self.window.doModal()

				return False
		except:
			Utils.log('Something nasty happened during login (' + str(sys.exc_info()[0]) + ')')
			xbmc.executebuiltin('Notification(An error occurred, Something nasty happened. Sorry...,3000,' + addon_path + '/resources/images/error.png)')
			return False

	def Logout(self):
		self.addon.setSetting('password', '')
		default.Api.Logout()

		return True
