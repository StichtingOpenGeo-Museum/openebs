import uwsgi
import psycopg2
import psycopg2.extras
import ujson as json
from operator import itemgetter
from settings.const import kv78_database_connect

COMMON_HEADERS = [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*'), ('Access-Control-Allow-Headers', 'Requested-With,Content-Type')]

def notfound(start_response):
	start_response('404 File Not Found', COMMON_HEADERS + [('Content-length', '2')])
	yield '[]'

def querylines(dataownercode):
    conn = psycopg2.connect(kv78_database_connect)
    cur = conn.cursor()
    cur.execute("""
SELECT
transporttype,
linepublicnumber,
dataownercode||'_'||lineplanningnumber as id,
linename
FROM
line
WHERE
dataownercode = %s
""",[dataownercode])
    reply = {'METRO' : [], 'BOAT' : [], 'TRAM' : [],'BUS' : []}

    lines = cur.fetchall()
    cur.close()
    conn.close()

    for line in lines:
        try:
            linenr = int(line[1])
        except:
            linenr = line[1]
            
        reply[line[0]].append([linenr, line[2], line[3]])

    for key in reply.keys():
        reply[key] = sorted(reply[key], key=itemgetter(0))
        reply[key] = [{'id': id, 'linenr': linenr, 'name': name} for linenr, id, name in reply[key]]
        if len(reply[key]) == 0:
            del reply[key]

    return json.dumps(reply)

def querylinesperstop(dataownercode):
    conn = psycopg2.connect(kv78_database_connect)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
select
jt.dataownercode||'_'||jt.userstopcodebegin as id,
timingpointname as name,
array_agg(distinct lineplanningnumber) as lines,
locationx_ew as x,
locationy_ns as y
FROM jopatiminglink as jt,usertimingpoint as u,timingpoint as t
WHERE
jt.dataownercode = u.dataownercode AND
jt.userstopcodebegin = u.userstopcode AND
t.dataownercode = u.timingpointdataownercode AND
t.timingpointcode = u.timingpointcode AND
jt.dataownercode = %s
group by jt.dataownercode,name,x,y,jt.userstopcodebegin
""",[dataownercode])
    reply = {}
    for row in cur.fetchall():
        reply[row['id']] = row
        del(row['id'])
    cur.close()
    conn.close()
    return json.dumps(reply)


def querystopinline(dataownercode,line):
    conn = psycopg2.connect(kv78_database_connect)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
SELECT DISTINCT on (id,direction)
jt.dataownercode||'_'||userstopcodebegin as id,
locationx_ew as x,
locationy_ns as y,
timingpointname as name,
linedirection as direction
FROM
jopatiminglink as jt,usertimingpoint as u,timingpoint as t,
(select distinct dataownercode,lineplanningnumber,journeypatterncode,linedirection from localservicegrouppasstime where dataownercode = %s and lineplanningnumber = %s) as jopa
--,userstop as us
WHERE
jt.dataownercode = u.dataownercode AND
jt.userstopcodebegin = u.userstopcode AND
u.timingpointcode = t.timingpointcode AND
jt.dataownercode = %s AND
jt.lineplanningnumber = %s AND
jopa.dataownercode = jt.dataownercode AND
jopa.lineplanningnumber = jt.lineplanningnumber AND
jopa.journeypatterncode = jt.journeypatterncode
--jt.dataownercode = us.dataownercode AND
--jt.userstopcodebegin = us.userstopcode
""",[dataownercode,line,dataownercode,line])
    reply = {}
    for row in cur.fetchall():
        if row['id'] in reply:
            reply[row['id']]['direction'].append(row['direction'])
        else:
            reply[row['id']] = row
            row['direction'] = [row['direction']]
            del(row['id'])
    cur.close()
    conn.close()
    return json.dumps(reply)
