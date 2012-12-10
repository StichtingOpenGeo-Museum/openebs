class MessageDurationType:
	REMOVE = 'REMOVE'
	FIRSTVEJO = 'FIRSTVEJO'
	ENDTIME = 'ENDTIME'

	def validate(self, value):
		return value in (self.REMOVE, self.FIRSTVEJO, self.ENDTIME)
