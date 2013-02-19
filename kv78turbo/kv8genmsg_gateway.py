#!/usr/bin/python
import zmq
from cStringIO import StringIO
from gzip import GzipFile
import sys
import psycopg2
import helper
from settings.const import kv15_database_connect
from settings.const import kv78_database_connect
from settings.const import kv8zmqpub
from datetime import datetime

context = zmq.Context()
kv8 = context.socket(zmq.SUB)

kv8.connect(kv8zmqpub)
kv8.setsockopt(zmq.SUBSCRIBE, "/GOVI/KV8genmsg")

processed = set([])
delete_processed = set([])

def log(row,conn=None,author=None,message=None,ipaddress=None):
    conn_created = False
    if conn is None:
        conn = psycopg2.connect(kv15_database_connect)
        conn_created = True
    cur = conn.cursor()
    cur.execute("""INSERT INTO kv15_log (timestamp,dataownercode,messagecodedate,messagecodenumber,author,message,ipaddress) VALUES (%s,%s,%s,%s,%s,%s,%s)""",[datetime.now(),row['DataOwnerCode'],row['MessageCodeDate'],row['MessageCodeNumber'],author,message,ipaddress])
    if conn_created:
        conn.commit()
        conn.close()

def fetchuserstopcode(dataownercode,timingpointcode):
    conn = psycopg2.connect(kv78_database_connect)
    cur = conn.cursor()
    cur.execute("SELECT dataownercode,userstopcode FROM usertimingpoint WHERE dataownercode = %s and timingpointcode = %s", 
[dataownercode,timingpointcode])
    row = cur.fetchone()
    if row is None:
        return (dataownercode,timingpointcode)
    cur.close()
    conn.close()
    return (row[0],row[1])

def processmessage(row):
    key = '_'.join(row[x] for x in ['DataOwnerCode','MessageCodeDate','MessageCodeNumber'])
    conn = psycopg2.connect(kv15_database_connect)
    if key not in processed:
      try:
        cur = conn.cursor()
    	cur.execute("""INSERT INTO kv15_stopmessage (dataownercode, messagetimestamp, messagecodedate, messagecodenumber, messagepriority, 
messagetype, messagedurationtype, messagecontent, reasontype, subreasontype, reasoncontent, effecttype, subeffecttype, effectcontent, measuretype, 
submeasuretype, measurecontent, advicetype, subadvicetype, advicecontent,messagestarttime,messageendtime) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""", (row['DataOwnerCode'], row['MessageTimeStamp'], row['MessageCodeDate'], row['MessageCodeNumber'], 'MISC', row['MessageType'], row['MessageDurationType'], row['MessageContent'], row['ReasonType'], row['SubReasonType'], row['ReasonContent'], row['EffectType'], row['SubEffectType'], row['EffectContent'], row['MeasureType'], row['SubMeasureType'], row['MeasureContent'], row['AdviceType'], row['SubAdviceType'], row['AdviceContent'], row['MessageStartTime'],row['MessageEndTime']))
        conn.commit()
        cur.close()
        log(row,author='KV8pubsub@govi.nu',message='KV8genmsg',ipaddress=kv8zmqpub)
        processed.add(key)
      except Exception as e:
        print e
        conn.rollback()
    dataownercode,userstopcode = fetchuserstopcode(row['DataOwnerCode'],row['TimingPointCode'])
    try:
        cur = conn.cursor()
        cur.execute("""INSERT INTO kv15_stopmessage_userstopcode (dataownercode, messagecodedate, messagecodenumber, userstopcode) VALUES (%s, %s, 
%s, %s)""", (dataownercode, row['MessageCodeDate'], row['MessageCodeNumber'], userstopcode))
        conn.commit()
        cur.close()
    except Exception as e:
        print e
        conn.rollback()
    conn.close()

def processdelmessage(row):
    key = '_'.join(row[x] for x in ['DataOwnerCode','MessageCodeDate','MessageCodeNumber'])
    conn = psycopg2.connect(kv15_database_connect)
    if key not in delete_processed:
      try:
        cur = conn.cursor()
	cur.execute("""UPDATE KV15_stopmessage SET messageendtime = now() WHERE dataownercode = %s AND messagecodedate = %s AND messagecodenumber = 
%s;""",[row['DataOwnerCode'], row['MessageCodeDate'], row['MessageCodeNumber']])
        conn.commit()
        cur.close()
        log(row,author='KV8pubsub@govi.nu',message='KV8genmsg_delete',ipaddress=kv8zmqpub)
        delete_processed.add(key)
      except Exception as e:
        print e
        conn.rollback()
    conn.close()

def recvPackage(content):
    for line in content.split('\r\n')[:-1]:
        if line[0] == '\\':
                # control characters
            if line[1] == 'G':
                label, name, subscription, path, endian, enc, res1, timestamp, _ = line[2:].split('|')
            elif line[1] == 'T':
                type = line[2:].split('|')[1]
            elif line[1] == 'L':
                keys = line[2:].split('|')
        else:
            row = {}
            values = line.split('|')
            for k,v in map(None, keys, values):
                if v == '\\0':
                    row[k] = None
                else:
                    row[k] = v
            if type == 'GENERALMESSAGEUPDATE':
                processmessage(row)
                print content
            elif type == 'GENERALMESSAGEDELETE':
                processdelmessage(row)
                print content

while True:
    multipart = kv8.recv_multipart()
    print multipart[0]
    content = GzipFile('','r',0,StringIO(''.join(multipart[1:]))).read()
    recvPackage(content)

