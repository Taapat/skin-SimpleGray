from enigma import iServiceInformation, iPlayableService

from Components.Converter.Converter import Converter
from Components.Element import cached


class SG_ServiceInfo(Converter):
	def __init__(self, type):
		Converter.__init__(self, type)

	@cached
	def get_text(self):

		def add_str(ret, text):
			return "%s %s" % (ret, text) if ret else text

		service = self.source.service
		info = service and service.info()
		if not info:
			return ""
		ret = ""
		audio = service.audioTracks()
		if audio:
			for i in range(audio.getNumberOfTracks()):
				description = audio.getTrackInfo(i).getDescription()
				if description and description.split()[0] in ("AC4", "AAC+", "AC3", "AC3+", "Dolby", "DTS", "DTS-HD", "HE-AAC", "WMA"):
					ret = "DOLBY"
					break
		if info.getInfo(iServiceInformation.sTXTPID) != -1:
			ret = add_str(ret, _("TEXT"))
		if service.subtitle().getSubtitleList():
			ret = add_str(ret, "SUB")
		video_height = info.getInfo(iServiceInformation.sVideoHeight)
		if video_height > 0:
			if video_height < 720:
				ret = add_str(ret, "SD")
			elif video_height >= 1500:
				ret = add_str(ret, "4K")
			else:
				ret = add_str(ret, "HD")
			ret = add_str(ret, "%sx%s" % (str(info.getInfo(iServiceInformation.sVideoWidth)), str(video_height)))
		return ret

	text = property(get_text)

	def changed(self, what):
		if what[0] == self.CHANGED_SPECIFIC and what[1] in (iPlayableService.evUpdatedInfo, iPlayableService.evVideoSizeChanged):
			Converter.changed(self, what)
