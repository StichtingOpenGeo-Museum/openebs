from io.push import Push

class KV15messages:
	def __init__(self, stopmessages = None):
		if stopmessages is None:
			self.stopmessages = []
		else:
			self.stopmessages = stopmessages
	
	def __str__(self):
		xml = """	<tmi8:KV15messages>\n"""
		for stopmessage in self.stopmessages:
			xml += str(stopmessage)
		xml += """	</tmi8:KV15messages>"""

		return xml
	
	def push(self, remote, path):
		return Push(dossiername='KV15messages', content = str(self)).push(remote, path)

