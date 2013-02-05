from datetime import datetime
from io.push import Push
class LineStopCancel():

    def __init__(self,dataownercode,lineplanningnumber,operatingday,lineplanningnumbers=None,userstops=None,timestamp=None,recover=False):
        self.dataownercode = dataownercode
        self.lineplanningnumbers = [lineplanningnumber]
        if lineplanningnumbers is not None:
            self.lineplanningnumbers = lineplanningnumbers
        self.operatingday = operatingday
        if userstops is not None:
            self.userstops = userstops
        else:
            self.userstops = []
        if timestamp is None:
            self.timestamp = datetime.now()
        else:
            self.timestamp = timestamp
        self.recover = recover

    def __str__(self):
        assert len(self.lineplanningnumbers) > 0
        data = {'dataownercode' : self.dataownercode, 'operatingday' : self.operatingday}
        str = """<KV17cvlinfo>
	<KV17JOURNEY>
		<dataownercode>%(dataownercode)s</dataownercode>
""" % data
        for lineplanningnumber in self.lineplanningnumbers:
            str += "		<lineplanningnumber>%(lineplanningnumber)s</lineplanningnumber>\n" % {'lineplanningnumber' : lineplanningnumber}
        str += """		<operatingday>%(operatingday)s</operatingday>
""" % data
        str += """	</KV17JOURNEY>
	<KV17MUTATEJOURNEYSTOP>
		<timestamp>%(timestamp)s</timestamp>
""" % {'timestamp' : self.timestamp.replace(microsecond=0).isoformat()}

        for userstop in self.userstops:
            if self.recover:
                stopline = """              <RECOVERLINE>
                        <userstopcode>%(userstopcode)s</userstopcode>
                        <passagesequencenumber>%(passageseqnumber)d</passagesequencenumber>
                </RECOVERLINE>
"""
            else:
                stopline = """		<SHORTENLINE>
			<userstopcode>%(userstopcode)s</userstopcode>
			<passagesequencenumber>%(passageseqnumber)d</passagesequencenumber>
		</SHORTENLINE>
""" 
            str += stopline % {'userstopcode' : userstop[0], 'passageseqnumber' : userstop[1] }

        str += """	</KV17MUTATEJOURNEYSTOP>
</KV17cvlinfo>"""
        return str

    def push(self, remote, path):
        return Push(dossiername='KV17cvlinfo', content = str(self), namespace='http://bison.connekt.nl/tmi8/kv17/msg').push(remote, path)
