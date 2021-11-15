"""
Minimal skin screens testing on enigma2 image.
Clone enigma2 image in folder ./enigma2 and start test with
PYTHONPATH=./test:./enigma2:./enigma2/lib/python python ./test/check_skin.py
"""

from __future__ import print_function

import inspect
import sys

import enigma


if sys.version_info[0] == 2:
	reload(sys)  # noqa: F821
	sys.setdefaultencoding('utf-8')


def try_screens_load():
	print('Try start session')
	session = enigma.start_session()

	print('=' * 60)
	print(' ' * 20 + 'Try screens load')
	print('=' * 60)

	screen_import = None

	for line in open('enigma2/data/SimpleGray-HD/skin_screens.xml', 'r').readlines():  # noqa: E501
		if '<!--from ' in line:
			screen_import = line.split('<!--', 1)[1].split('-->', 1)[0]
			continue
		if screen_import and '<screen name=' in line:
			screen_name = line.split('name="', 1)[1].split('"', 1)[0]
			screen_import = '%s import %s' % (screen_import, screen_name)
			try:
				exec(screen_import)
			except Exception as er:
				print('Error in', screen_import, er)
			else:
				try:
					args = inspect.getargspec(eval(screen_name).__init__)[0][2:]
					session.open(eval(screen_name), *args)
				except Exception as er:
					print('Error in', screen_name, er)
			screen_import = None
			print('=' * 60)


try_screens_load()
