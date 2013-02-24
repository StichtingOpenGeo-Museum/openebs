from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta

import ujson as json
import pytz
import psycopg2
import psycopg2.extras
from xml.sax.saxutils import escape

from enum.messagepriority import MessagePriority
from enum.messagetype import MessageType
from enum.messagedurationtype import MessageDurationType
from enum.reason import ReasonType
from enum.reason import SubReasonType
from enum.effect import EffectType
from enum.effect import SubEffectType
from enum.measure import MeasureType
from enum.measure import SubMeasureType
from enum.advice import AdviceType
from enum.advice import SubAdviceType

from kv15.deletemessage import DeleteMessage

from settings.const import kv15_database_connect

class StopMessage():
    def _next_messagecodenumber(self):
        #try:
        #    serial = int(open('/tmp/serial.txt', 'r').read()) + 1
        #except:
        #    serial = 0

        #open('/tmp/serial.txt', 'w').write(str(serial))

        #return serial
        conn = psycopg2.connect(kv15_database_connect)
        cur = conn.cursor()
        cur.execute("""SELECT nextval('messagecodenumber');""")
        return cur.fetchall()[0][0]

    def __init__(self, dataownercode='openOV', messagecodedate=None, messagecodenumber=None,userstopcodes=[], lineplanningnumbers=None, 
                 messagepriority=MessagePriority.PTPROCESS,messagetype=MessageType.GENERAL, messagedurationtype=MessageDurationType.ENDTIME, 
                 messagestarttime=None, messageendtime=None, messagecontent='', 
                 reasontype=ReasonType.ONGEDEFINIEERD, subreasontype=SubReasonType.ONBEKEND, reasoncontent='', 
                 effecttype=EffectType.ONGEDEFINIEERD, subeffecttype=SubEffectType.ONBEKEND, effectcontent='',
                 measuretype=MeasureType.ONGEDEFINIEERD, submeasuretype=SubMeasureType.GEEN, measurecontent='',
                 advicetype=AdviceType.ONGEDEFINIEERD, subadvicetype=SubAdviceType.GEEN, advicecontent='', messagetimestamp=None):

        self.dataownercode = dataownercode
        if messagecodedate is None:
            self.messagecodedate = date.today()
        else:
            self.messagecodedate = messagecodedate

        self.messagecodenumber = messagecodenumber
        self.userstopcodes = userstopcodes
        self.messagepriority = messagepriority
        self.messagetype = messagetype
        self.messagedurationtype = messagedurationtype

        if messagestarttime is None:
            self.messagestarttime = datetime.now()
        else:
            self.messagestarttime = messagestarttime
        if messageendtime is None:
            self.messageendtime = datetime.combine(date.today() + timedelta(days = 1), time(4, 0, 0))
        else:
            self.messageendtime = messageendtime

        self.messagecontent = messagecontent

        self.reasontype = reasontype
        self.subreasontype = subreasontype
        self.reasoncontent = reasoncontent


        self.effecttype = effecttype
        self.subeffecttype = subeffecttype
        self.effectcontent = effectcontent

        self.measuretype = measuretype
        self.submeasuretype = submeasuretype
        self.measurecontent = measurecontent

        self.advicetype = advicetype
        self.subadvicetype = subadvicetype
        self.advicecontent = advicecontent
        
        if messagetimestamp is None:
            self.messagetimestamp = datetime.now()
        else:
            self.messagetimestamp = messagetimestamp

    def __str__(self):
        if len(self.userstopcodes) == 0:
            raise NameError('UserStopCodes == 0')

        if self.messagecodenumber is None:
            self.messagecodenumber = self._next_messagecodenumber()

        data = {'dataownercode': self.dataownercode,
                'messagetimestamp': pytz.timezone('Europe/Amsterdam').localize(self.messagetimestamp.replace(microsecond=0)).isoformat(),
                'messagecodedate': self.messagecodedate,
                'messagecodenumber': self.messagecodenumber,
                'messagepriority': self.messagepriority,
                'messagetype': self.messagetype,
                'messagedurationtype': self.messagedurationtype,
                'messagestarttime': pytz.timezone('Europe/Amsterdam').localize(self.messagestarttime.replace(microsecond=0)).isoformat(),
                'messageendtime': pytz.timezone('Europe/Amsterdam').localize(self.messageendtime.replace(microsecond=0)).isoformat(),
                'messagecontent': escape(self.messagecontent),
                'reasontype': self.reasontype,
                'subreasontype': self.subreasontype,
                'reasoncontent': escape(self.reasoncontent),
                'effecttype': self.effecttype,
                'subeffecttype': self.subeffecttype,
                'effectcontent': escape(self.effectcontent),
                'measuretype': self.measuretype,
                'submeasuretype': self.submeasuretype,
                'measurecontent': escape(self.measurecontent),
                'advicetype': self.advicetype,
                'subadvicetype': self.subadvicetype,
                'advicecontent': escape(self.advicecontent)}

        xml = """               <STOPMESSAGE>
                <dataownercode>%(dataownercode)s</dataownercode>
                <messagecodedate>%(messagecodedate)s</messagecodedate>
                <messagecodenumber>%(messagecodenumber)d</messagecodenumber>
                <userstopcodes>\n""" % data

        for userstopcode in self.userstopcodes:
            xml += """                              <userstopcode>%(userstopcode)s</userstopcode>\n""" % {'userstopcode': userstopcode}

        xml += """                      </userstopcodes>
                <messagepriority>%(messagepriority)s</messagepriority>
                <messagetype>%(messagetype)s</messagetype>
                <messagedurationtype>%(messagedurationtype)s</messagedurationtype>
                <messagestarttime>%(messagestarttime)s</messagestarttime>
                <messageendtime>%(messageendtime)s</messageendtime>
                <messagecontent>%(messagecontent)s</messagecontent>\n""" % data

        if self.reasontype != ReasonType.ONGEDEFINIEERD:
            xml += """                      <reasontype>%(reasontype)s</reasontype>
                    <subreasontype>%(subreasontype)s</subreasontype>
                    <reasoncontent>%(reasoncontent)s</reasoncontent>\n""" % data

        if self.effecttype != EffectType.ONGEDEFINIEERD:
            xml += """                      <effecttype>%(effecttype)s</effecttype>
            <subeffecttype>%(subeffecttype)s</subeffecttype>
            <effectcontent>%(effectcontent)s</effectcontent>\n""" % data

        if self.measuretype != MeasureType.ONGEDEFINIEERD:
            """                     <measuretype>%(measuretype)s</measuretype>
            <submeasuretype>%(submeasuretype)s</submeasuretype>
            <measurecontent>%(measurecontent)s</measurecontent>\n""" % data

        if self.advicetype != AdviceType.ONGEDEFINIEERD:
            """                     <advicetype>%(advicetype)s</advicetype>
            <subadvicetype>%(subadvicetype)s</subadvicetype>
            <advicecontent>%(advicecontent)s</advicecontent>\n""" % data

        xml += """                      <messagetimestamp>%(messagetimestamp)s</messagetimestamp>
        </STOPMESSAGE>\n""" % data
        
        return xml

    def delete(self):
        return DeleteMessage(dataownercode = self.dataownercode, messagecodedate = self.messagecodedate, messagecodenumber = self.messagecodenumber)

    def update(self, row):
        dataownercode, messagecodedate, messagecodenumber, userstopcodes, lineplanningnumbers, messagepriority, messagetype, messagedurationtype, messagestarttime, messageendtime, messagecontent, reasontype, subreasontype, reasoncontent, effecttype, subeffecttype, effectcontent, measuretype, submeasuretype, measurecontent, advicetype, subadvicetype, advicecontent, messagetimestamp = row
        self.dataownercode  = row['dataownercode'];
        self.messagecodedate  = row['messagecodedate'];
        self.messagecodenumber  = row['messagecodenumber'];
        self.userstopcodes  = row['userstopcodes'];
        self.lineplanningnumbers  = row['lineplanningnumbers'];
        self.messagepriority  = row['messagepriority'];
        self.messagetype  = row['messagetype'];
        self.messagedurationtype  = row['messagedurationtype'];
        self.messagestarttime  = row['messagestarttime'];
        self.messageendtime  = row['messageendtime'];
        self.messagecontent  = row['messagecontent'];
        self.reasontype  = row['reasontype'];
        self.subreasontype  = row['subreasontype'];
        self.reasoncontent  = row['reasoncontent'];
        self.effecttype  = row['effecttype'];
        self.subeffecttype  = row['subeffecttype'];
        self.effectcontent  = row['effectcontent'];
        self.measuretype  = row['measuretype'];
        self.submeasuretype  = row['submeasuretype'];
        self.measurecontent  = row['measurecontent'];
        self.advicetype  = row['advicetype'];
        self.subadvicetype  = row['subadvicetype'];
        self.advicecontent  = row['advicecontent'];
        self.messagetimestamp  = row['messagetimestamp'];

    def load(self, dataownercode, messagecodedate, messagecodenumber, conn=None):
        if conn is None:
            conn = psycopg2.connect(kv15_database_connect)

        cur = conn.cursor()
        
        cur.execute("""select dataownercode, messagecodedate, messagecodenumber, 
        (select string_agg(userstopcode, '|') as userstopcodes from kv15_stopmessage_userstopcode where dataownercode = kv15_stopmessage.dataownercode and messagecodedate = kv15_stopmessage.messagecodedate and messagecodenumber = kv15_stopmessage.messagecodenumber group by dataownercode, messagecodedate, messagecodenumber),
        (select string_agg(lineplanningnumber, '|') as lineplanningnumbers from kv15_stopmessage_lineplanningnumber where dataownercode = kv15_stopmessage.dataownercode and messagecodedate = kv15_stopmessage.messagecodedate and messagecodenumber = kv15_stopmessage.messagecodenumber group by dataownercode, messagecodedate, messagecodenumber),
        messagepriority, messagetype, messagedurationtype, messagestarttime, messageendtime, messagecontent, reasontype, subreasontype, reasoncontent, effecttype, subeffecttype, effectcontent, measuretype, submeasuretype, measurecontent, advicetype, subadvicetype, advicecontent, messagetimestamp
        from kv15_stopmessage where isdeleted = false and dataownercode = %s and messagecodedate = %s and messagecodenumber = %s LIMIT 1;""", (dataownercode, messagecodedate, messagecodenumber,));

        output = cur.fetchall()
        for row in output:
            row['userstopcodes'] = row['userstopcodes'].split('|')
            row['lineplanningnumbers'] = row['lineplanningnumbers'].split('|')
            
            self.update(row)

    def overview(self, dataownercode, conn=None):
        if conn is None:
            conn = psycopg2.connect(kv15_database_connect)

        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cur.execute("""
SELECT 
dataownercode,
cast(messagecodedate as text),
cast(messagecodenumber as int),
(     SELECT array_agg(userstopcode) as userstopcodes FROM kv15_stopmessage_userstopcode 
	WHERE dataownercode = kv15_stopmessage.dataownercode and messagecodedate = kv15_stopmessage.messagecodedate 
              and messagecodenumber = kv15_stopmessage.messagecodenumber group by dataownercode, messagecodedate, messagecodenumber),
(	SELECT array_agg(lineplanningnumber) as lineplanningnumbers FROM kv15_stopmessage_lineplanningnumber 
	WHERE dataownercode = kv15_stopmessage.dataownercode and messagecodedate = kv15_stopmessage.messagecodedate 
		and messagecodenumber = kv15_stopmessage.messagecodenumber group by dataownercode, messagecodedate, messagecodenumber),
messagepriority, messagetype, messagedurationtype, 
to_char(messagestarttime, 'DD-MM-YYYY HH24:MI:SS') as messagestarttime,to_char(messageendtime, 'DD-MM-YYYY HH24:MI:SS') as messageendtime,
messagecontent, cast(reasontype as int), subreasontype, reasoncontent,
cast(effecttype as int), subeffecttype, effectcontent, cast(measuretype as int),submeasuretype,
measurecontent, cast(advicetype as int), subadvicetype, advicecontent, cast(messagetimestamp as text),(current_timestamp < messageendtime) as isactive
FROM kv15_stopmessage
WHERE isdeleted = FALSE AND dataownercode = %s AND messagescenario IS NULL AND (current_timestamp < messageendtime)
UNION
(SELECT 
dataownercode,
cast(messagecodedate as text),
cast(messagecodenumber as int),
(     SELECT array_agg(userstopcode) as userstopcodes FROM kv15_stopmessage_userstopcode 
	WHERE dataownercode = kv15_stopmessage.dataownercode and messagecodedate = kv15_stopmessage.messagecodedate 
              and messagecodenumber = kv15_stopmessage.messagecodenumber group by dataownercode, messagecodedate, messagecodenumber),
(	SELECT array_agg(lineplanningnumber) as lineplanningnumbers FROM kv15_stopmessage_lineplanningnumber 
	WHERE dataownercode = kv15_stopmessage.dataownercode and messagecodedate = kv15_stopmessage.messagecodedate 
		and messagecodenumber = kv15_stopmessage.messagecodenumber group by dataownercode, messagecodedate, messagecodenumber),
messagepriority, messagetype, messagedurationtype, 
to_char(messagestarttime, 'DD-MM-IYYY HH24:MI:SS') as messagestarttime,to_char(messageendtime, 'DD-MM-IYYY HH24:MI:SS') as messageendtime,
messagecontent, cast(reasontype as int), subreasontype, reasoncontent,
cast(effecttype as int), subeffecttype, effectcontent, cast(measuretype as int),submeasuretype,
measurecontent, cast(advicetype as int), subadvicetype, advicecontent, cast(messagetimestamp as text),(current_timestamp < messageendtime) as isactive
FROM kv15_stopmessage
WHERE isdeleted = FALSE AND dataownercode = %s AND messagescenario IS NULL AND (current_timestamp > messageendtime)
 ORDER BY messagetimestamp DESC LIMIT 50)
ORDER by isactive DESC ,messagetimestamp DESC""", (dataownercode,dataownercode));

        output = cur.fetchall()
        for row in output:
	    if row['userstopcodes'] is None:
                row['userstopcodes'] = []
        return json.dumps(output)
    
    def delete_scenario(self, dataownercode, scenario, conn=None):
        if conn is None:
            conn = psycopg2.connect(kv15_database_connect)

        cur = conn.cursor()
        
        if scenario is not None:
            cur.execute("update kv15_stopmessage set isdeleted = true where dataownercode = %s and messagescenario = %s;", (dataownercode, scenario,));
            conn.commit()
            
        conn.close()

    def overview_scenario(self, dataownercode, scenario=None, conn=None):
        if conn is None:
            conn = psycopg2.connect(kv15_database_connect)

        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        if scenario is None:
            cur.execute("""
SELECT
msgs.dataownercode,
messagescenario,
array_agg(distinct userstopcode) as userstopcodes,
array_agg(distinct lineplanningnumber) as lineplanningnumbers
FROM kv15_stopmessage_userstopcode as stops,  kv15_stopmessage as msgs LEFT JOIN kv15_stopmessage_lineplanningnumber as linenumbers USING 
(dataownercode,messagecodedate,messagecodenumber)
WHERE
msgs.dataownercode = stops.dataownercode AND 
msgs.messagecodedate = stops.messagecodedate AND
msgs.messagecodenumber = stops.messagecodenumber AND
isdeleted = false AND
msgs.dataownercode = %s AND
messagescenario IS NOT NULL
GROUP BY msgs.dataownercode, messagescenario
ORDER BY messagescenario""", (dataownercode,));
        else:
            cur.execute("""
SELECT 
dataownercode,
cast(messagecodedate as text),
cast(messagecodenumber as int),
(     SELECT array_agg(userstopcode) as userstopcodes FROM kv15_stopmessage_userstopcode 
	WHERE dataownercode = kv15_stopmessage.dataownercode and messagecodedate = kv15_stopmessage.messagecodedate 
              and messagecodenumber = kv15_stopmessage.messagecodenumber group by dataownercode, messagecodedate, messagecodenumber),
(	SELECT array_agg(lineplanningnumber) as lineplanningnumbers FROM kv15_stopmessage_lineplanningnumber 
	WHERE dataownercode = kv15_stopmessage.dataownercode and messagecodedate = kv15_stopmessage.messagecodedate 
		and messagecodenumber = kv15_stopmessage.messagecodenumber group by dataownercode, messagecodedate, messagecodenumber),
messagepriority, messagetype, messagedurationtype, 
to_char(messagestarttime, 'DD-MM-IYYY HH24:MI:SS') as messagestarttime,to_char(messageendtime, 'DD-MM-IYYY HH24:MI:SS') as messageendtime,
messagecontent, cast(reasontype as int), subreasontype, reasoncontent,
cast(effecttype as int), subeffecttype, effectcontent, cast(measuretype as int),submeasuretype,
measurecontent, cast(advicetype as int), subadvicetype, advicecontent, cast(messagetimestamp as text),(current_timestamp < messageendtime) as isactive
FROM kv15_stopmessage
WHERE isdeleted = FALSE AND dataownercode = %s AND messagescenario = %s;""", (dataownercode, scenario))

        output = cur.fetchall()
        for row in output:
	    if row['userstopcodes'] is None:
	        row['userstopcodes'] = []
            if row['lineplanningnumbers'] is not None and len(row['lineplanningnumbers']) > 0 and row['lineplanningnumbers'][0] is None:
                row['lineplanningnumbers'] = None
	if scenario is not None:
	        return json.dumps({'messages': output})
	
	# TODO: this is ugly
	return json.dumps(output)
	

    def save(self, conn=None, messagescenario=None):
        conn_created = False
        if conn is None:
            conn = psycopg2.connect(kv15_database_connect)
            conn_created = True
        cur = conn.cursor()
        if self.messagecodenumber is None:
            self.messagecodenumber = self._next_messagecodenumber()

	if messagescenario is None:
	        cur.execute("""INSERT INTO kv15_stopmessage (dataownercode, messagetimestamp, messagecodedate, messagecodenumber, messagepriority, messagetype, messagedurationtype, messagestarttime, messageendtime, messagecontent, reasontype, subreasontype, reasoncontent, effecttype, subeffecttype, effectcontent, measuretype, submeasuretype, measurecontent, advicetype, subadvicetype, advicecontent) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""", (self.dataownercode, self.messagetimestamp.replace(microsecond=0).isoformat(), self.messagecodedate, self.messagecodenumber, self.messagepriority, self.messagetype, self.messagedurationtype, self.messagestarttime.replace(microsecond=0).isoformat(), self.messageendtime.replace(microsecond=0).isoformat(), self.messagecontent, self.reasontype, self.subreasontype, self.reasoncontent, self.effecttype, self.subeffecttype, self.effectcontent, self.measuretype, self.submeasuretype, self.measurecontent, self.advicetype, self.subadvicetype, self.advicecontent,))
	else:
	        cur.execute("""INSERT INTO kv15_stopmessage (dataownercode, messagetimestamp, messagecodedate, messagecodenumber, messagepriority, messagetype, messagedurationtype, messagecontent, reasontype, subreasontype, reasoncontent, effecttype, subeffecttype, effectcontent, measuretype, submeasuretype, measurecontent, advicetype, subadvicetype, advicecontent, messagescenario) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""", (self.dataownercode, self.messagetimestamp.replace(microsecond=0).isoformat(), self.messagecodedate, self.messagecodenumber, self.messagepriority, self.messagetype, self.messagedurationtype, self.messagecontent, self.reasontype, self.subreasontype, self.reasoncontent, self.effecttype, self.subeffecttype, self.effectcontent, self.measuretype, self.submeasuretype, self.measurecontent, self.advicetype, self.subadvicetype, self.advicecontent, messagescenario))

        for userstopcode in self.userstopcodes:
            cur.execute("""INSERT INTO kv15_stopmessage_userstopcode (dataownercode, messagecodedate, messagecodenumber, userstopcode) VALUES (%s, %s, %s, %s)""", (self.dataownercode, self.messagecodedate, self.messagecodenumber, userstopcode))
        if conn_created:
            conn.commit()
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
