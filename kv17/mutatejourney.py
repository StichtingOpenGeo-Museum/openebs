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
                self.recovered = False
		self.canceled = False
                self.mutations = []

	def cancel(self):
		self.canceled = True
		self.recovered  = False
		self.mutation = []
		return self

	def recover(self):
		self.canceled = False
		self.recovered = True
		return self

        def journeyxml(self):
		return """	<KV17cvlinfo>
		<KV17JOURNEY>
			<dataownercode>%s</dataownercode>
			<lineplanningnumber>%s</lineplanningnumber>
			<operatingday>%s</operatingday>
			<journeynumber>%d</journeynumber>
			<reinforcementnumber>%d</reinforcementnumber>
		</KV17JOURNEY>\n""" % (self.dataownercode,self.lineplanningnumber,self.operatingday,int(self.journeynumber),int(self.reinforcementnumber))

	def __str__(self):
		xml = self.journeyxml()
		if self.canceled:
			xml += """		<KV17MUTATEJOURNEY>
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
			return xml #We never expect to find other mutations when you're canceling the whole trip
		if self.recovered:
			xml += """		<KV17MUTATEJOURNEY>
			<timestamp>%s</timestamp>
			<RECOVER/>
		</KV17MUTATEJOURNEY>\n""" % (self.timestamp.replace(microsecond=0).isoformat())
                if len(self.mutations) > 0:
			xml+=  '		<KV17MUTATEJOURNEYSTOP>\n'
			xml+=  '			<timestamp>%s</timestamp>\n' % (self.timestamp.replace(microsecond=0).isoformat())
			for mutation in self.mutations:
				xml += '			<%s>\n' % (mutation['type'])
				for key,value in mutation.items():
					if key == 'type':
						continue
					xml += '				<%s>%s</%s>\n' % (key,value,key)
				xml += '			</%s>\n' % (mutation['type'])
			xml += '		</KV17MUTATEJOURNEYSTOP>\n'
		return xml + '	</KV17cvlinfo>'

	def push(self, remote, path):
		return Push(dossiername='KV17cvlinfo', content = str(self), namespace='http://bison.connekt.nl/tmi8/kv17/msg').push(remote, path)

	def shorten(self,userstopcode,passagesequencenumber=0):
                mutation = {	'type' : 'SHORTEN',
				'userstopcode' : userstopcode,
				'passagesequencenumber' : passagesequencenumber}
		self.mutations.append(mutation)
		return self

	def changepasstimes(self,userstopcode,targetarrivaltime,targetdeparturetime,journeystoptype,passagesequencenumber=0):
                mutation = {	'type' : 'CHANGEDESTINATION',
				'userstopcode' : userstopcode,
				'passagesequencenumber' : passagesequencenumber,
				'targetarrivaltime' : targetarrivaltime,
				'targetdeparturetime' : targetdeparturetime,
				'journeystoptype' : journeystoptype}
		self.mutations.append(mutation)
		return self

	def changedestination(self,userstopcode,destinationcode,destinationname50,destinationname16,passagesequencenumber=0):
                mutation = {	'type' : 'CHANGEDESTINATION',
				'userstopcode' : userstopcode,
				'passagesequencenumber' : passagesequencenumber,
				'destinationcode' : destinationcode,
				'destinationname50' : destinationname50,
				'destinationname16' : destinationname16}
		self.mutations.append(mutation)
		return self
  		    
	def mutationmessage(self,userstopcode,passagesequencenumber=0):
                mutation = {	'type' : 'MUTATIONMESSAGE',
				'userstopcode' : userstopcode,
				'passagesequencenumber' : passagesequencenumber,
				'reasontype' : self.reasontype,
				'subreasontype' : self.subreasontype,
				'reasoncontent' : escape(self.reasoncontent),
				'advicetype' : self.advicetype,
				'subadvicetype' : self.subadvicetype,
				'advicecontent' : escape(self.advicecontent)}
		self.mutations.append(mutation)
		return self

