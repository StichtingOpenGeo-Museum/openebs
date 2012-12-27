from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta

# TODO delete moet database informeren

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

		xml = """		<DELETEMESSAGE>
			<dataownercode>%(dataownercode)s</dataownercode>
			<messagecodedate>%(messagecodedate)s</messagecodedate>
			<messagecodenumber>%(messagecodenumber)d</messagecodenumber>
		</DELETEMESSAGE>\n""" % data

		return xml


