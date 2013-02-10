from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta

class DeleteMessage():
	def __init__(self, dataownercode='openOV', messagecodedate=None, messagecodenumber=None):
		self.dataownercode = dataownercode

		if messagecodedate is None:
			self.messagecodedate = None
		else:
			self.messagecodedate = messagecodedate

		if messagecodenumber is None:
			self.messagecodenumber = None
		else:
			self.messagecodenumber = messagecodenumber

	def __str__(self):
		if self.messagecodedate is None or self.messagecodenumber is None:
			raise NameError('MessageCodeDate or MessageCodeNumber is None')

		data = {'dataownercode': self.dataownercode,
			'messagecodedate': self.messagecodedate,
			'messagecodenumber': self.messagecodenumber}

		xml = """		<DELETEMESSAGE>
			<dataownercode>%(dataownercode)s</dataownercode>
			<messagecodedate>%(messagecodedate)s</messagecodedate>
			<messagecodenumber>%(messagecodenumber)d</messagecodenumber>
		</DELETEMESSAGE>\n""" % data

		return xml

        def save(self, conn=None, messagescenario=None):
                conn_created = False
                if conn is None:
                        conn = psycopg2.connect(kv15_database_connect)
                        conn_created = True

		cur = conn.cursor()

		cur.execute("""UPDATE KV15_stopmessage SET messageendtime = now() WHERE dataownercode = %s AND messagecodedate = %s AND messagecodenumber = %s;""",[self.dataownercode, self.messagecodedate, self.messagecodenumber])
                if conn_created:
                        conn.close()

        def log(self,conn=None,author=None,message=None,ipaddress=None):
            conn_created = False
            if conn is None:
                conn = psycopg2.connect(kv15_database_connect)
                conn_created = True
            cur = conn.cursor()
            cur.execute("""INSERT INTO kv15_log (timestamp,dataownercode,messagecodedate,messagecodenumber,author,message,ipaddress) VALUES (%s,%s,%s,%s,%s,%s,%s)""",[datetime.now(),self.dataownercode,self.messagecodedate,self.messagecodenumber,author,message,ipaddress])
            if conn_created:
                conn.commit()
                conn.close()
