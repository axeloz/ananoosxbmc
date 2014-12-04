#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
   Ananoos plugin for XBMC
   Copyright (C) 2014 Axel de Vignon
   License: Apache 2.0 (See license.txt)
'''


import sys
import xbmc
import xbmcvfs
import xbmcgui
import xbmcplugin
import xbmcaddon
import time
import urllib
import re
import urlparse


# XBMC hooks
xbmc_version= xbmc.getInfoLabel('System.BuildVersion')
xbmc_date	= xbmc.getInfoLabel('System.BuildDate')
addon		= xbmcaddon.Addon(id='plugin.video.ananoos')
language	= addon.getLocalizedString
addon_path	= addon.getAddonInfo('path');
debug		= True
base_url	= sys.argv[0]
addon_handle= int(sys.argv[1])
args		= urlparse.parse_qs(sys.argv[2][1:])
mode		= args.get('mode', None)


# Plugin constants
version		= "0.1"
plugin		= "Ananoos/" + version
author		= "Axel de Vignon"
url			= "www.ananoos.com"
API_URL		= 'http://www.ananoos.com/api'


# Importing our librairies
import resources.lib.Auth as Auth
Auth = Auth.Auth()
import resources.lib.Utils as Utils	
import resources.lib.Api as Api
Api = Api.Api()



#Auth.Logout()
#Auth.Login()

def browse():
	xbmcplugin.setContent(addon_handle, 'movies')
	xbmcplugin.addSortMethod(addon_handle, 1)

	# Get current folder UID
	parent = args.get('parent', None)
	if parent is None:
		parent = '0'
	else:
		parent = str(parent[0])


	# Building API URL
	Utils.log('Getting items from API')

	try:
		content = Api.Browse(parent=parent)
		if content and content['list']:
			# Adding items to the listing
			for item in content['list']:
				# Item is a folder
				if item['type'] == 'dir':
					# Building URL
					url = base_url + '?' + urllib.urlencode({
						'mode' : 'browse', 
						'parent': item['id']
					})					

					Utils.log('Adding folder to list: '+url)
					li = xbmcgui.ListItem(item['name'], iconImage='DefaultFolder.png')
					xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
				else:
					# Item is a regular file
					url = base_url + '?' + urllib.urlencode({
						'mode' : 'stream',
						'file': item['id']
					})				

					li = xbmcgui.ListItem(item['name'], iconImage='DefaultVideo.png')
					Utils.log('Adding file to list: '+url)
					xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
		xbmcplugin.endOfDirectory(addon_handle)
	except:
		Utils.log('Error when listing items')
		xbmc.executebuiltin('Notification('+language(30021)+', '+language(30022)+',3000,' + addon_path + '/resources/images/error.png)')
	

def stream():
	item_id = args.get('file', '0')
	Utils.log('Getting stream URL for file id: '+item_id[0])

	content = Api.getStreamUrl(item_id[0])
	if content and content['result'] == True:
		player = xbmc.Player()
		Utils.log('Stream URL is: '+content['url'])

		content['url'] = content['url'] + '|User-Agent='+urllib.quote(Utils.getUserAgent())+'&'

		# Sending cookies with the query
		cookies = Api.getCookies()
		if len(cookies) > 0:
			content['url'] = content['url'] + 'Cookie='
			for i in cookies:
				content['url'] = content['url'] + urllib.quote(i + '=' + cookies[i]+';')

		# Starting the playback
		player.play(content['url'])

		# If video doesn't work, raising an error
		time.sleep(3)
		if not player.isPlayingVideo():
			xbmc.executebuiltin('Notification('+language(30019)+', '+language(30020)+',3000,' + addon_path + '/resources/images/error.png)')
		
	else:
		xbmc.executebuiltin('Notification('+language(30019)+', '+language(30020)+',3000,' + addon_path + '/resources/images/error.png)')


def logout():
	Auth.logout()


''' Now routing '''
if mode is None or mode[0] == 'browse':
	browse()
elif mode[0] == 'stream':
	stream()
elif mode[0] == 'logout':
	logout()