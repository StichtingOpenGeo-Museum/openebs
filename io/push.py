from datetime import datetime
from httplib import HTTPConnection
from settings.const import debug, send

class Push:
	def __init__(self, subscriberid = 'openOV', dossiername = None, content = None, namespace = None):
		self.subscriberid = subscriberid
		self.timestamp = datetime.now()
		
		self.dossiername = dossiername
		self.content = content
		self.namespace = namespace
	
	def __str__(self):
		data = {'namespace': self.namespace,
		        'subscriberid': self.subscriberid,
			'dossiername': self.dossiername,
		        'timestamp': self.timestamp.replace(microsecond=0).isoformat(),
			'content': self.content }

		xml = """<VV_TM_PUSH xmlns="%(namespace)s">
	<SubscriberID>%(subscriberid)s</SubscriberID>
	<Version>8.1.0.1</Version>
	<DossierName>%(dossiername)s</DossierName>
	<Timestamp>%(timestamp)s</Timestamp>
%(content)s
</VV_TM_PUSH>""" % data

		return xml
	
	def push(self, remote, path):
		content = str(self)
		if debug:
			print content

		if send:
			conn = HTTPConnection(remote)
			conn.request("POST", path, content, {"Content-type": "application/xml"})
			response = conn.getresponse()
			data = response.read()
			conn.close()
			if debug:
				print data

			return data
		
		return None
