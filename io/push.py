from datetime import datetime
from httplib import HTTPConnection
from settings.const import debug

class Push:
	def __init__(self, subscriberid = 'openOV', dossiername = None, content = None):
		self.subscriberid = subscriberid
		self.timestamp = datetime.now()
		
		self.dossiername = dossiername
		self.content = content
	
	def __str__(self):
		data = {'subscriberid': self.subscriberid,
			'dossiername': self.dossiername,
		        'timestamp': self.timestamp.replace(microsecond=0).isoformat(),
			'content': self.content }

		xml = """<tmi8:VV_TM_PUSH xsi:schemaLocation="http://bison.connekt.nl/tmi8/kv15/msg kv15-msg.xsd" xmlns:tmi8c="http://bison.connekt.nl/tmi8/kv15/core" xmlns:tmi8="http://bison.connekt.nl/tmi8/kv15/msg" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
	<tmi8:SubscriberID>%(subscriberid)s</tmi8:SubscriberID>
	<tmi8:Version>8.1.0.1</tmi8:Version>
	<tmi8:DossierName>%(dossiername)s</tmi8:DossierName>
	<tmi8:Timestamp>%(timestamp)s</tmi8:Timestamp>
%(content)s
</tmi8:VV_TM_PUSH>""" % data

		return xml
	
	def push(self, remote, path):
		content = str(self)
		if debug:
			print content

		conn = HTTPConnection(remote)
		conn.request("POST", path, content, {"Content-type": "application/xml"})
		response = conn.getresponse()
		data = response.read()
		conn.close()

		return data
