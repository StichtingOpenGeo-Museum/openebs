from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta

from xml.sax.saxutils import escape

from enum.messagepriority import MessagePriority
from enum.messagetype import MessageType
from enum.messagedurationtype import MessageDurationType
from enum.reason import ReasonType
from enum.reason import SubReasonType
from enum.effect import EffectType
from enum.effect import SubEffectType
from enum.measure import MeasureType
from enum.measure import SubMeasureType
from enum.advice import AdviceType
from enum.advice import SubAdviceType

from kv15.deletemessage import DeleteMessage

#from settings.const import database_connect

class StopMessage():
	def _next_messagecodenumber(self):
		try:
			serial = int(open('/tmp/serial.txt', 'r').read()) + 1
		except:
			serial = 0

		open('/tmp/serial.txt', 'w').write(str(serial))

		return serial
#		try:
#			conn = psycopg2.connect(database_connect)
#			cur = conn.cursor()
#			cur.execute("""SELECT nextval('messagecodenumber');""")
#			return cur.fetchall()[0][0]
#		except:
#			return None

	def __init__(self, dataownercode='openOV', messagecontent=None, userstopcodes=None):

		self.dataownercode = dataownercode
		self.messagecodedate = date.today()
		self.messagecodenumber = self._next_messagecodenumber()

		if userstopcodes is None:
			self.userstopcodes = []
		else:
			self.userstopcodes = userstopcodes
		
		self.messagepriority = MessagePriority.PTPROCESS
		self.messagetype = MessageType.GENERAL
		self.messagedurationtype = MessageDurationType.ENDTIME

		self.messagestarttime = datetime.now()
		self.messageendtime = datetime.combine(date.today() + timedelta(days = 1), time(4, 0, 0))

		if messagecontent is None:
			self.messagecontent = ''
		else:
			self.messagecontent = messagecontent

		self.reasontype = ReasonType.ONGEDEFINIEERD
		self.subreasontype = SubReasonType.ONBEKEND
		self.reasoncontent = ''

		self.effecttype = EffectType.ONGEDEFINIEERD
		self.subeffecttype = SubEffectType.ONBEKEND
		self.effectcontent = ''

		self.measuretype = MeasureType.ONGEDEFINIEERD
		self.submeasuretype = SubMeasureType.GEEN
		self.measurecontent = ''
		
		self.advicetype = AdviceType.ONGEDEFINIEERD
		self.subadvicetype = SubAdviceType.GEEN
		self.advicecontent = ''

		self.messagetimestamp = datetime.now()
	
	def __str__(self):
		if len(self.userstopcodes) == 0:
			raise NameError('UserStopCodes == 0')

		data = {'dataownercode': self.dataownercode,
			'messagetimestamp': self.messagetimestamp.replace(microsecond=0).isoformat(),
			'messagecodedate': self.messagecodedate,
			'messagecodenumber': self.messagecodenumber,
			'messagepriority': self.messagepriority,
			'messagetype': self.messagetype,
			'messagedurationtype': self.messagedurationtype,
			'messagestarttime': self.messagestarttime.replace(microsecond=0).isoformat(),
			'messageendtime': self.messageendtime.replace(microsecond=0).isoformat(),
			'messagecontent': escape(self.messagecontent),
			'reasontype': self.reasontype,
			'subreasontype': self.subreasontype,
			'reasoncontent': escape(self.reasoncontent),
			'effecttype': self.effecttype,
			'subeffecttype': self.subeffecttype,
			'effectcontent': escape(self.effectcontent),
			'measuretype': self.measuretype,
			'submeasuretype': self.submeasuretype,
			'measurecontent': escape(self.measurecontent),
			'advicetype': self.advicetype,
			'subadvicetype': self.subadvicetype,
			'advicecontent': escape(self.advicecontent)}

		xml = """		<STOPMESSAGE>
			<dataownercode>%(dataownercode)s</dataownercode>
			<messagecodedate>%(messagecodedate)s</messagecodedate>
			<messagecodenumber>%(messagecodenumber)d</messagecodenumber>
			<userstopcodes>\n""" % data

		for userstopcode in self.userstopcodes:
			xml += """				<userstopcode>%(userstopcode)s</userstopcode>\n""" % {'userstopcode': userstopcode}

		xml += """			</userstopcodes>
			<messagepriority>%(messagepriority)s</messagepriority>
			<messagetype>%(messagetype)s</messagetype>
			<messagedurationtype>%(messagedurationtype)s</messagedurationtype>
			<messagestarttime>%(messagestarttime)s</messagestarttime>
			<messageendtime>%(messageendtime)s</messageendtime>
			<messagecontent>%(messagecontent)s</messagecontent>\n""" % data

		if self.reasontype != ReasonType.ONGEDEFINIEERD:
			xml += """			<reasontype>%(reasontype)s</reasontype>
				<subreasontype>%(subreasontype)s</subreasontype>
				<reasoncontent>%(reasoncontent)s</reasoncontent>\n""" % data

		if self.effecttype != EffectType.ONGEDEFINIEERD:
			xml += """			<effecttype>%(effecttype)s</effecttype>
			<subeffecttype>%(subeffecttype)s</subeffecttype>
			<effectcontent>%(effectcontent)s</effectcontent>\n""" % data

		if self.measuretype != MeasureType.ONGEDEFINIEERD:
			"""			<measuretype>%(measuretype)s</measuretype>
			<submeasuretype>%(submeasuretype)s</submeasuretype>
			<measurecontent>%(measurecontent)s</measurecontent>\n""" % data

		if self.advicetype != AdviceType.ONGEDEFINIEERD:
			"""			<advicetype>%(advicetype)s</advicetype>
			<subadvicetype>%(subadvicetype)s</subadvicetype>
			<advicecontent>%(advicecontent)s</advicecontent>\n""" % data

		xml += """			<messagetimestamp>%(messagetimestamp)s</messagetimestamp>
		</STOPMESSAGE>\n""" % data

		return xml

	def delete(self):
		return DeleteMessage(dataownercode = self.dataownercode, messagecodedate = self.messagecodedate, messagecodenumber = self.messagecodenumber)
