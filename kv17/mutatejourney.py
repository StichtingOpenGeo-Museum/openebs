from datetime import datetime
from xml.sax.saxutils import escape

from enum.reason import ReasonType
from enum.reason import SubReasonType
from enum.advice import AdviceType
from enum.advice import SubAdviceType
from io.push import Push

class MutateJourney():
	def __init__(self, dataownercode, lineplanningnumber,journeynumber,operatingday,reinforcementnumber=0):
		self.dataownercode = dataownercode
		self.lineplanningnumber = lineplanningnumber
		self.operatingday = operatingday
		self.journeynumber = journeynumber
		self.reinforcementnumber = reinforcementnumber
		self.timestamp = datetime.now()

		self.reasontype = ReasonType.ONGEDEFINIEERD
		self.subreasontype = SubReasonType.ONBEKEND
		self.reasoncontent = ''
		
		self.advicetype = AdviceType.ONGEDEFINIEERD
		self.subadvicetype = SubAdviceType.GEEN
		self.advicecontent = ''

        def journeyxml(self):
		return """	<KV17cvlinfo>
		<KV17JOURNEY>
			<dataownercode>%s</dataownercode>
			<lineplanningnumber>%s</lineplanningnumber>
			<operatingday>%s</operatingday>
			<journeynumber>%d</journeynumber>
			<reinforcementnumber>%d</reinforcementnumber>
		</KV17JOURNEY>\n""" % (self.dataownercode,self.lineplanningnumber,self.operatingday,int(self.journeynumber),int(self.reinforcementnumber))

	def cancel(self,remote, path):
                xml = self.journeyxml() + """		<KV17MUTATEJOURNEY>
			<timestamp>%s</timestamp>
			<CANCEL>\n""" % (self.timestamp.replace(microsecond=0).isoformat())
		if self.reasontype != ReasonType.ONGEDEFINIEERD:
			xml += """				<reasontype>%s</reasontype>
				<subreasontype>%s</subreasontype>
				<reasoncontent>%s</reasoncontent>\n""" % (self.reasontype,self.subreasontype,escape(self.reasoncontent))
		if self.advicetype != AdviceType.ONGEDEFINIEERD:
			xml += """				<advicetype>%s</advicetype>
				<subadvicetype>%s</subadvicetype>
				<advicecontent>%s</advicecontent>\n""" % (self.advicetype,self.subadvicetype,escape(self.advicecontent))
                xml += '			</CANCEL>\n		</KV17MUTATEJOURNEY>\n	</KV17cvlinfo>'
		return Push(dossiername='KV17cvlinfo', content = xml,namespace='http://bison.connekt.nl/tmi8/kv17/msg').push(remote, path)

	def recover(self,remote,path):
                xml = self.journeyxml() + """		<KV17MUTATEJOURNEY>
			<timestamp>%s</timestamp>
			<RECOVER/>
		</KV17MUTATEJOURNEY>\n	</KV17cvlinfo>""" % (self.timestamp.replace(microsecond=0).isoformat())
		return Push(dossiername='KV17cvlinfo', content = xml,namespace='http://bison.connekt.nl/tmi8/kv17/msg').push(remote, path)
