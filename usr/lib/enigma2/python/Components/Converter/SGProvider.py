#
# Return provider name in channel selection
# Code based on converter ServiceName2.py
# By Taapat (c) 2015
#

from enigma import eServiceReference, eServiceCenter
from Components.Converter.Converter import Converter
from Components.Element import cached
from Screens.ChannelSelection import service_types_radio, service_types_tv


class SGProvider(Converter, object):
	def __init__(self, type):
		Converter.__init__(self, type)

	@cached
	def getText(self):
		ref = self.source.service
		if isinstance(ref, eServiceReference):
			if ref.getData(0) in (2,10):
				typestr = service_types_radio
			else:
				typestr = service_types_tv
			serviceHandler = eServiceCenter.getInstance()
			providerlist = serviceHandler.list(eServiceReference(
				'%s (channelID == %08x%04x%04x) && %s FROM PROVIDERS ORDER BY name' %
					(typestr[:20],
					ref.getUnsignedData(4), # NAMESPACE
					ref.getUnsignedData(2), # TSID
					ref.getUnsignedData(3), # ONID
					typestr[20:])))
			if providerlist is not None:
				while True:
					provider = providerlist.getNext()
					if not provider.valid():
						break
					if provider.flags & eServiceReference.isDirectory:
						servicelist = serviceHandler.list(provider)
						if servicelist is not None:
							while True:
								service = servicelist.getNext()
								if not service.valid():
									break
								if service == ref:
									info = serviceHandler.info(provider)
									if info:
										return info.getName(provider)
									return ""
		return ""

	text = property(getText)

	def changed(self, what):
		if what[0] is not self.CHANGED_SPECIFIC:
			Converter.changed(self, what)

