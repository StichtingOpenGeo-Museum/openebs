class MessagePriority:
	CALAMITY = 'CALAMITY'
	PTPROCESS = 'PTPROCESS'
	COMMERCIAL = 'COMMERCIAL'
	MISC = 'MISC'

	def validate(self, value):
		return value in (self.CALAMITY, self.PTPROCESS, self.COMMERCIAL, self.MISC)
