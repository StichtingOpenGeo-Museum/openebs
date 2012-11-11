from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta

#from settings.const import database_connect

class DeleteMessage():
	def __init__(self, dataownercode='openOV', messagecodedate=None, messagecodenumber=None):
		self.dataownercode = dataownercode

		if messagecodedate is None:
			self.messagecodedate = None
		else:
			self.messagecodedate = messagecodedate

		if messagecodenumber is None:
			self.messagecodenumber = None
		else:
			self.messagecodenumber = messagecodenumber

	def __str__(self):
		if self.messagecodedate is None or self.messagecodenumber is None:
			raise NameError('MessageCodeDate or MessageCodeNumber is None')

		data = {'dataownercode': self.dataownercode,
			'messagecodedate': self.messagecodedate,
			'messagecodenumber': self.messagecodenumber}

		xml = """		<tmi8:DELETEMESSAGE>
			<tmi8:dataownercode>%(dataownercode)s</tmi8:dataownercode>
			<tmi8:messagecodedate>%(messagecodedate)s</tmi8:messagecodedate>
			<tmi8:messagecodenumber>%(messagecodenumber)d</tmi8:messagecodenumber>
		</tmi8:DELETEMESSAGE>\n""" % data

		return xml


