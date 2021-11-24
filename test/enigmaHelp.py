def ngettext(singular, plural, n):
	return singular


globals()['__builtins__']['ngettext'] = ngettext


class _eInstances:
	def __setattr__(self, name, value, *args):
		self.__dict__[name] = value


class _eConsoleAppContainer:
	def __init__(self):
		self.dataAvail = []
		self.appClosed = []

	def __getattr__(self, attr):
		def default(*args):
			return 0
		return default


class _eTimer:
	def __init__(self):
		self.callback = []
		self.timeout = _eInstances()
		self.timeout.callback = []
		self.callback_thread = None

	def start_callback(self, singleshot):
		for f in self.timeout.callback:
			f()
		for f in self.callback:
			if singleshot and f in self.callback:
				self.callback.remove(f)
			f()

	def start(self, msec, singleshot=False):
		if int(msec) == 1000:
			from threading import Thread
			self.callback_thread = Thread(target=self.start_callback,
					args=(singleshot,))
			self.callback_thread.start()
		else:
			self.start_callback(singleshot)

	def startLongTimer(self, sec):
		self.start_callback(True)

	def stop(self):
		self.callback_thread = None
