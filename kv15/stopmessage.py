from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta

import json
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
        try:
            serial = int(open('/tmp/serial.txt', 'r').read()) + 1
        except:
            serial = 0

        open('/tmp/serial.txt', 'w').write(str(serial))

        return serial

        # conn = psycopg2.connect(kv15_database_connect)
        # cur = conn.cursor()
        # cur.execute("""SELECT nextval('messagecodenumber');""")
        # return cur.fetchall()[0][0]

    def __init__(self, dataownercode=None, messagecodedate=None, messagecodenumber=None, userstopcodes=None, lineplanningnumbers=None, messagepriority=None, messagetype=None, messagedurationtype=None, messagestarttime=None, messageendtime=None, messagecontent=None, reasontype=None, subreasontype=None, reasoncontent=None, effecttype=None, subeffecttype=None, effectcontent=None, measuretype=None, submeasuretype=None, measurecontent=None, advicetype=None, subadvicetype=None, advicecontent=None, messagetimestamp=None):

        if dataownercode is None:
            self.dataownercode = 'openOV'

        if messagecodedate is None:
            self.messagecodedate = date.today()

        if messagecodenumber is None:
            self.messagecodenumber = None

        if userstopcodes is None:
            self.userstopcodes = []
        else:
            self.userstopcodes = userstopcodes

        if messagepriority is None:
            self.messagepriority = MessagePriority.PTPROCESS

        if messagetype is None:
            self.messagetype = MessageType.GENERAL

        if messagedurationtype is None:
            self.messagedurationtype = MessageDurationType.ENDTIME

        if messagestarttime is None:
            self.messagestarttime = datetime.now()

        if messageendtime is None:
            self.messageendtime = datetime.combine(date.today() + timedelta(days = 1), time(4, 0, 0))

        if messagecontent is None:
            self.messagecontent = ''
        else:
            self.messagecontent = messagecontent

        if reasontype is None:
            self.reasontype = ReasonType.ONGEDEFINIEERD
        if subreasontype is None:
            self.subreasontype = SubReasonType.ONBEKEND
        if reasoncontent is None:
            self.reasoncontent = ''

        if effecttype is None:
            self.effecttype = EffectType.ONGEDEFINIEERD
        if subeffecttype is None:
            self.subeffecttype = SubEffectType.ONBEKEND
        if effectcontent is None:
            self.effectcontent = ''

        if measuretype is None:
            self.measuretype = MeasureType.ONGEDEFINIEERD
        if submeasuretype is None:
            self.submeasuretype = SubMeasureType.GEEN
        if measurecontent is None:
            self.measurecontent = ''

        if advicetype is None:
            self.advicetype = AdviceType.ONGEDEFINIEERD
        if subadvicetype is None:
            self.subadvicetype = SubAdviceType.GEEN
        if advicecontent is None:
            self.advicecontent = ''

        if messagetimestamp is None:
            self.messagetimestamp = datetime.now()

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
        from kv15_stopmessage where dataownercode = %s and messagecodedate = %s and messagecodenumber = %s LIMIT 1;""", (dataownercode, messagecodedate, messagecodenumber,));

        output = cur.fetchall()
        for row in output:
            row['userstopcodes'] = row['userstopcodes'].split('|')
            row['lineplanningnumbers'] = row['lineplanningnumbers'].split('|')
            
            self.update(row)

    def overview(self, dataownercode, conn=None):
        if conn is None:
            conn = psycopg2.connect(kv15_database_connect)

        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cur.execute("""select dataownercode, messagecodedate, messagecodenumber, 
        (select string_agg(userstopcode, '|') as userstopcodes from kv15_stopmessage_userstopcode where dataownercode = kv15_stopmessage.dataownercode and messagecodedate = kv15_stopmessage.messagecodedate and messagecodenumber = kv15_stopmessage.messagecodenumber group by dataownercode, messagecodedate, messagecodenumber),
        (select string_agg(lineplanningnumber, '|') as lineplanningnumbers from kv15_stopmessage_lineplanningnumber where dataownercode = kv15_stopmessage.dataownercode and messagecodedate = kv15_stopmessage.messagecodedate and messagecodenumber = kv15_stopmessage.messagecodenumber group by dataownercode, messagecodedate, messagecodenumber),
        messagepriority, messagetype, messagedurationtype, messagestarttime, messageendtime, messagecontent, reasontype, subreasontype, reasoncontent, effecttype, subeffecttype, effectcontent, measuretype, submeasuretype, measurecontent, advicetype, subadvicetype, advicecontent, messagetimestamp
        from kv15_stopmessage where dataownercode = %s LIMIT 50;""", (dataownercode,));

        output = cur.fetchall()
        for row in output:
            row['userstopcodes'] = row['userstopcodes'].split('|')
            row['lineplanningnumbers'] = row['lineplanningnumbers'].split('|')

        return json.dumps(output)

    def save(self, conn=None):
        if conn is None:
            conn = psycopg2.connect(kv15_database_connect)

        cur = conn.cursor()

        cur.execute("""INSERT INTO KV15messages (dataownercode, messagetimestamp, messagecodedate, messagecodenumber, messagepriority, messagetype, messagedurationtype, messagestarttime, messageendtime, messagecontent, reasontype, subreasontype, reasoncontent, effecttype, subeffecttype, effectcontent, measuretype, submeasuretype, measurecontent, advicetype, subadvicetype, advicecontent) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""", (self.dataownercode, self.messagetimestamp.replace(microsecond=0).isoformat(), self.messagecodedate, self.messagecodenumber, self.messagepriority, self.messagetype, self.messagedurationtype, self.messagestarttime.replace(microsecond=0).isoformat(), self.messageendtime.replace(microsecond=0).isoformat(), self.messagecontent, self.reasontype, self.subreasontype, self.reasoncontent, self.effecttype, self.subeffecttype, self.effectcontent, self.measuretype, self.submeasuretype, self.measurecontent, self.advicetype, self.subadvicetype, self.advicecontent,))
        for userstopcode in self.userstopcodes:
            cur.execute("""INSERT INTO KV15messages (dataownercode, messagecodedate, messagecodenumber, userstopcode) VALUES (%s, %s, %s, %s)""", (self.dataownercode, self.messagecodedate, self.messagecodenumber, userstopcode))
