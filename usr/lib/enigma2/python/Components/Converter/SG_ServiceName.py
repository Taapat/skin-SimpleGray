from enigma import iServiceInformation, iPlayableService

from Components.Converter.Converter import Converter
from Components.Element import cached


class SG_ServiceName(Converter):
	def __init__(self, type):
		Converter.__init__(self, type)

	@cached
	def get_text(self):
		service = self.source.service
		info = service and service.info()
		if not info:
			return ""
		ref = self.source.serviceref
		num = ref and ref.getChannelNum()
		num_prov = "%s %s" % (
			num and str(num) or "",
			info.getInfoString(iServiceInformation.sProvider)
		)
		if len(num_prov) < 10:
			num_prov = "  " * (10 - len(num_prov)) + num_prov
		return r"\c00ffffff%s \c008f8f8f%s" % (
			num_prov,
			info.getName().replace("\xc2\x86", "").replace("\xc2\x87", "").replace("_", " ")
		)

	text = property(get_text)

	def changed(self, what):
		if what[0] == self.CHANGED_SPECIFIC and what[1] == iPlayableService.evStart:
			Converter.changed(self, what)
