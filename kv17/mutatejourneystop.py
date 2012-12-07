from datetime import datetime
from xml.sax.saxutils import escape

from enum.reason import ReasonType
from enum.reason import SubReasonType
from enum.advice import AdviceType
from enum.advice import SubAdviceType
from io.push import Push

class MutateJourneyStop():
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
                self.mutations = []

        def journeyxml(self):
		return """\t<KV17cvlinfo>
\t\t<KV17JOURNEY>
\t\t\t\t<dataownercode>%s</dataownercode>
\t\t\t\t<lineplanningnumber>%s</lineplanningnumber>
\t\t\t\t<operatingday>%s</operatingday>
\t\t\t\t<journeynumber>%d</journeynumber>
\t\t\t\t<reinforcementnumber>%d</reinforcementnumber>
\t\t</KV17JOURNEY>\n""" % (self.dataownercode,self.lineplanningnumber,self.operatingday,int(self.journeynumber),int(self.reinforcementnumber))

	def __str__(self):
		xml = self.journeyxml() + '\t\t<KV17MUTATEJOURNEYSTOP>\n'
		for mutation in self.mutations:
			xml += '\t\t\t<%s>\n' % (mutation['type'])
			for key,value in mutation.items():
				if key == 'type':
					continue
				xml += '\t\t\t\t<%s>%s</%s>\n' % (key,value,key)
			xml += '\t\t\t</%s>\n' % (mutation['type'])
		xml += '\t\t</KV17MUTATEJOURNEYSTOP>\n'
		return xml + '\t</KV17cvlinfo>'

	def push(self, remote, path):
		return Push(dossiername='KV17cvlinfo', content = str(self), namespace='http://bison.connekt.nl/tmi8/kv17/msg').push(remote, path)

	def shorten(self,userstopcode,passagesequencenumber=0):
                mutation = {	'type' : 'SHORTEN',
				'timestamp' : self.timestamp.replace(microsecond=0).isoformat(),
				'userstopcode' : userstopcode,
				'passagesequencenumber' : passagesequencenumber}
		self.mutations.append(mutation)

	def changepasstimes(self,userstopcode,targetarrivaltime,targetdeparturetime,journeystoptype,passagesequencenumber=0):
                mutation = {	'type' : 'CHANGEDESTINATION',
				'timestamp' : self.timestamp.replace(microsecond=0).isoformat(),
				'userstopcode' : userstopcode,
				'passagesequencenumber' : passagesequencenumber,
				'targetarrivaltime' : targetarrivaltime,
				'targetdeparturetime' : targetdeparturetime,
				'journeystoptype' : journeystoptype}
		self.mutations.append(mutation)

	def changedestination(self,userstopcode,destinationcode,destinationname50,destinationname16,passagesequencenumber=0):
                mutation = {	'type' : 'CHANGEDESTINATION',
				'timestamp' : self.timestamp.replace(microsecond=0).isoformat(),
				'userstopcode' : userstopcode,
				'passagesequencenumber' : passagesequencenumber,
				'destinationcode' : destinationcode,
				'destinationname50' : destinationname50,
				'destinationname16' : destinationname16}
		self.mutations.append(mutation)
  		    
	def mutationmessage(self,userstopcode,passagesequencenumber=0):
                mutation = {	'type' : 'MUTATIONMESSAGE',
				'timestamp' : self.timestamp.replace(microsecond=0).isoformat(),
				'userstopcode' : userstopcode,
				'passagesequencenumber' : passagesequencenumber,
				'reasontype' : self.reasontype,
				'subreasontype' : self.subreasontype,
				'reasoncontent' : escape(self.reasoncontent),
				'advicetype' : self.advicetype,
				'subadvicetype' : self.subadvicetype,
				'advicecontent' : escape(self.advicecontent)}
		self.mutations.append(mutation)

