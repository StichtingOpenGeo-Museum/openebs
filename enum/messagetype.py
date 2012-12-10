class MessageType:
	GENERAL = 'GENERAL'
	ADDITIONAL = 'ADDITIONAL'
	OVERRULE = 'OVERRULE'
	BOTTOMLINE = 'BOTTOMLINE'

	def validate(self.value):
		return value in (self.GENERAL, self.ADDITIONAL, self.OVERRULE, self.BOTTOMLINE)
