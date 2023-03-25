"""
Minimal skin screens testing on enigma2 image.
"""
import sys
from inspect import signature
from traceback import print_exc

import enigma
import eConsoleImpl
import eBaseImpl

import enigmaHelp  # noqa: F401


enigma.eTimer = eBaseImpl.eTimer
enigma.eSocketNotifier = eBaseImpl.eSocketNotifier
enigma.eConsoleAppContainer = eConsoleImpl.eConsoleAppContainer


class Session:
	def __init__(self, desktop=None, navigation=None):
		print('Session init')
		self.desktop = desktop
		self.nav = navigation
		self.current_dialog = None
		self.dialog_stack = []
		self.summary = None
		from Screens.SessionGlobals import SessionGlobals
		self.screen = SessionGlobals(self)

	def execBegin(self, first=True, do_show=True):
		c = self.current_dialog
		try:
			c.execBegin()
		except IndexError:
			pass

	def instantiateDialog(self, screen, *arguments, **kwargs):
		return self.doInstantiateDialog(screen, arguments, kwargs, self.desktop)

	def doInstantiateDialog(self, screen, arguments, kwargs, desktop):
		# create dialog
		dlg = screen(self, *arguments, **kwargs)
		# read skin data
		from skin import readSkin
		readSkin(dlg, None, dlg.skinName, desktop)
		# create GUI view of this dialog
		dlg.setDesktop(desktop)
		dlg.applySkin()
		return dlg

	def pushCurrent(self):
		if self.current_dialog is not None:
			self.dialog_stack.append((self.current_dialog, self.current_dialog.shown))
			self.current_dialog.execEnd()

	def openWithCallback(self, callback, screen, *arguments, **kwargs):
		print('OpenWithCallback')
		dlg = self.open(screen, *arguments, **kwargs)
		dlg.callback = callback
		return dlg

	def open(self, screen, *arguments, **kwargs):
		print('Session open ', screen, arguments)
		self.pushCurrent()
		dlg = self.current_dialog = self.instantiateDialog(screen, *arguments, **kwargs)

		dlg.callback = None
		self.execBegin()
		return dlg

	def close(self, screen, *retval):
		print('Session close', screen)
		assert screen == self.current_dialog
		self.current_dialog.execEnd()
		callback = self.current_dialog.callback
		del self.current_dialog.callback

		if self.dialog_stack:
			(self.current_dialog, do_show) = self.dialog_stack.pop()
			self.execBegin(first=False, do_show=do_show)
		else:
			self.current_dialog = None

		if callback is not None:
			callback(*retval)


if sys.version_info[0] == 2:
	reload(sys)  # noqa: F821
	sys.setdefaultencoding('utf-8')


def new_activateLanguage(self, index):
	if index not in self.lang:
		print('Selected language does not exist, fallback to de_DE!')
		index = 'de_DE'
	self.lang[index] = ('Deutsch', 'de', 'DE', 'ISO-8859-15')
	self.activeLanguage = index
	print('Activating language de_DE')


def start_session():
	print('init session')

	print('init language')
	from Components.Language import Language, language
	Language.activateLanguage = new_activateLanguage
	language.activateLanguage('de_DE')

	print('init simple summary')
	from Screens import InfoBar  # noqa: F401
	from Screens.SimpleSummary import SimpleSummary  # noqa: F401

	print('init parental')
	import Components.ParentalControl
	Components.ParentalControl.InitParentalControl()

	print('init nav')
	from Navigation import Navigation

	print('init usage')
	import Components.UsageConfig
	Components.UsageConfig.InitUsageConfig()

	print('init skin')
	import skin
	skin.loadSkinData(enigma.getDesktop(0))

	print('init av')
	import Components.AVSwitch
	Components.AVSwitch.InitAVSwitch()

	print('init misc')
	from Components.config import config, ConfigYesNo, ConfigInteger
	config.misc.RestartUI = ConfigYesNo(default=False)
	config.misc.prev_wakeup_time = ConfigInteger(default=0)
	config.misc.prev_wakeup_time_type = ConfigInteger(default=0)
	config.misc.startCounter = ConfigInteger(default=0)

	print('init keymapparser')
	import keymapparser
	keymapparser.readKeymap(config.usage.keymap.value)

	return Session(enigma.getDesktop(1), Navigation())


def try_screens_load():
	print('Try start session')
	session = start_session()

	print('=' * 60)
	print(' ' * 20 + 'Try screens load')
	print('=' * 60)

	screen_import = None
	before = []
	errors = []

	for line in open('./data/SimpleGray-HD/skin_screens.xml', 'r').readlines():  # noqa: E501
		if '<!--before ' in line:
			before.append(line.split('<!--before ', 1)[1].split('-->', 1)[0])
			continue
		elif before:
			for action in before:
				try:
					exec(action)
				except Exception as er:
					error = 'Error in action %s: %s' % (action, er)
					print(error)
					errors.append(error)
			before = []
			print('=' * 60)
		if '<!--from ' in line:
			screen_import = line.split('<!--', 1)[1].split('-->', 1)[0]
			continue
		if screen_import and '<screen name=' in line:
			screen_name = line.split('name="', 1)[1].split('"', 1)[0]
			screen_import = '%s import %s' % (screen_import, screen_name)
			try:
				exec(screen_import)
			except Exception as er:
				error = 'Error in %s: %s' % (screen_import, er)
				print(error)
				errors.append(error)
			else:
				arg_spec = signature(eval(screen_name).__init__).parameters.values()
				if len(arg_spec) < 3:
					args = ()
				else:
					args = ('' for i, x in enumerate(arg_spec) if x.default == x.empty and i > 1)
				try:
					src_screen = eval(screen_name)
					src = session.open(src_screen, *args)
				except Exception as er:
					error = 'Error in %s: %s\n%s' % (screen_name, er, signature(eval(screen_name).__init__))
					print(error)
					errors.append(error)
					print_exc()
				else:
					src.close(src_screen)
			screen_import = None
			print('=' * 60)
	for er in errors:
		print(er)
	print(len(errors), 'errors in screens test')


try_screens_load()
