from __future__ import print_function

import os

from enigma import ePixmap

from Components.Harddisk import harddiskmanager
from Components.Renderer.Renderer import Renderer
from Tools.Directories import pathExists


searchPaths = []


if pathExists('/tmp/piconProv/'):
	piconInTmp = True
	lastPiconPath = '/tmp/piconProv/'
	print('[PiconProv] use path:', lastPiconPath)
else:
	piconInTmp = False
	lastPiconPath = None


def initPiconPaths():
	global searchPaths
	searchPaths = []
	for mp in ('/tmp/', '/media/hdd/', '/usr/share/enigma2/', '/'):
		onMountpointAdded(mp)
	for part in harddiskmanager.getMountedPartitions():
		onMountpointAdded(part.mountpoint)


def onMountpointAdded(mountpoint):
	global searchPaths
	piconPath = os.path.join(mountpoint, 'piconProv') + '/'
	if os.path.isdir(piconPath) and piconPath not in searchPaths:
		for fn in os.listdir(piconPath):
			if fn[-4:] == '.png' or fn[-4:] == '.svg':
				print("[PiconProv] adding path:", piconPath)
				searchPaths.append(piconPath)
				break


def onMountpointRemoved(mountpoint):
	global searchPaths
	path = os.path.join(mountpoint, 'piconProv') + '/'
	if path in searchPaths:
		searchPaths.remove(path)
		print('[PiconProv] removed path:', path)


def onPartitionChange(why, part):
	if why == 'add':
		onMountpointAdded(part.mountpoint)
	elif why == 'remove':
		onMountpointRemoved(part.mountpoint)


def findPicon(serviceName):
	global lastPiconPath
	if lastPiconPath:
		for ext in ('.png', '.svg'):
			pngname = lastPiconPath + serviceName + ext
			if pathExists(pngname):
				return pngname
	if not piconInTmp:
		for piconPath in searchPaths:
			for ext in ('.png', '.svg'):
				pngname = piconPath + serviceName + ext
				if pngname:
					if pathExists(pngname):
						lastPiconPath = piconPath
						return pngname
	return None


def getPiconName(serviceName):
	if not serviceName or serviceName == 'Unknown':
		return None
	sname = serviceName.upper()
	pngname = findPicon(sname)
	return pngname


class SG_PiconProv(Renderer):
	def __init__(self):
		Renderer.__init__(self)
		self.pngname = ''

	def addPath(self, value):
		if pathExists(value):
			global searchPaths
			if value[-1] != '/':
				value += '/'
			if value not in searchPaths:
				searchPaths.append(value)

	def applySkin(self, desktop, parent):
		attribs = self.skinAttributes[:]
		for (attrib, value) in self.skinAttributes:
			if attrib == 'path':
				self.addPath(value)
				attribs.remove((attrib, value))
		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)

	GUI_WIDGET = ePixmap

	def changed(self, what):
		if self.instance:
			pngname = None
			if what[0] != self.CHANGED_CLEAR:
				pngname = getPiconName(self.source.text)
			if self.pngname is not pngname:
				if pngname:
					self.instance.setScale(1)
					self.instance.setPixmapFromFile(pngname)
					self.instance.show()
				else:
					self.instance.hide()
				self.pngname = pngname


if not piconInTmp:
	harddiskmanager.on_partition_list_change.append(onPartitionChange)
	initPiconPaths()
