#!/usr/bin/env python2

import psycopg2
from datetime import date

conn = psycopg2.connect("dbname=kv78turbo1")
cur = conn.cursor()

def getJourneyPatternPriority(operationdate, dataownercode, lineplanningnumber):
    cur.execute("select p.linedirection, p.localservicelevelcode, p.journeypatterncode, max(userstopordernumber) as priority from localservicegroupvalidity as v, localservicegrouppasstime as p where v.dataownercode = p.dataownercode and v.localservicelevelcode = p.localservicelevelcode and v.operationdate = %s and v.dataownercode = %s and lineplanningnumber = %s group by p.localservicelevelcode, p.journeypatterncode, p.linedirection order by localservicelevelcode, priority desc, linedirection;", (operationdate, dataownercode, lineplanningnumber) )
    return cur.fetchall()

def alignOneDirectionJourneyPatterns(data, dataownercode):
    coalesce = ', '.join(['q%d.userstopcode' % (order) for order, _query in data])
    over = ', '.join(['q%d.userstopordernumber' % (order) for order, _query in data])

    part = "SELECT agg.projection, agg.myorder, t.stopareacode FROM (SELECT COALESCE(%s) AS projection, row_number() OVER(ORDER BY %s) AS myorder, %s FROM %s" % (coalesce, over, coalesce, data[0][1]) 
    for order, query in data[1:]:
        part += ' FULL JOIN %s ON q%d.userstopcode = q%d.userstopcode' % (query, data[0][0], order)

    part += ") AS agg, usertimingpoint AS u, timingpoint AS t WHERE u.dataownercode = '%s' AND agg.projection = u.userstopcode AND u.timingpointdataownercode = t.dataownercode AND u.timingpointcode = t.timingpointcode" % (dataownercode)

    return part

def alignJourneyPatternsSQL(operationdate, dataownercode, lineplanningnumber):
    priorities = getJourneyPatternPriority(operationdate, dataownercode, lineplanningnumber)
    if len(priorities) == 0:
        return

    data = {1: [], 2: []}
    highest = priorities[0][0]
    order = 0

    for linedirection, localservicelevelcode, journeypatterncode, priority in priorities:
        order += 1
        data[linedirection].append((order, "(select distinct userstopcode, userstopordernumber from localservicegrouppasstime as p where dataownercode = '%s' and localservicelevelcode = '%s' and journeypatterncode = '%s') as q%d" % (dataownercode, localservicelevelcode, journeypatterncode, order)))

    sql_one = alignOneDirectionJourneyPatterns(data[highest], dataownercode)

    second = data[(set(data.keys()) - set([highest])).pop()]
    if len(second) > 0:
        sql_two = alignOneDirectionJourneyPatterns(second, dataownercode)
        sql = "SELECT one.*, two.* FROM (%s) AS one FULL JOIN (%s) AS two ON one.stopareacode = two.stopareacode ORDER BY one.myorder, two.myorder desc;" % (sql_one, sql_two)
    else:
        sql = sql_one

    cur.execute(sql)
    return cur.fetchall()

def alignJourneyPatterns(operationdate, dataownercode, lineplanningnumber):
    patterns = alignJourneyPatternsSQL(operationdate, dataownercode, lineplanningnumber)

    if patterns is None:
        return

    if len(patterns[0]) == 3:
        return [(x[0]) for x in patterns]

    max_one = None
    max_two = None
    order = 0;

    final = {}
    todo = {}
    output = []

    for pattern in patterns:
        order += 1
        max_one = max(max_one, pattern[1])
        max_two = max(max_two, pattern[4])
        expect_two = None

        if pattern[0] and pattern[3]:
            final[order] = ([pattern[0:3], pattern[3:6]])
            last_two = int(pattern[4] - 1)
        elif pattern[0]:
            final[order] = ([pattern[0:3], last_two])
            last_two -= 1
        elif pattern[0] is None:
            done = False
            for key, x in final.items():
                if type(x[1]) is int and x[1] == int(pattern[4]):
                    final[key][1] = pattern[3:6]
                    done = True
                    break                    

            if not done:
                todo[int(pattern[4])] = pattern[3:6]

    first = todo.keys()
    for _key, x in final.items():
        if len(first) > 0:
            if type(x[1]) is int:
                if x[1] < first[0]:
                    output.append((None, todo[first[0]]))
                    del todo[first[0]]
                    first = todo.keys()
            elif x[1][1] < first[0]:
                output.append((None, todo[first[0]]))
                del todo[first[0]]
                first = todo.keys()

        if (type(x[1]) is int):
            output.append((x[0], None))

        else:
            output.append((x[0], x[1]))

    return output

def printAligned(aligned):
    if len(aligned[0]) == 2:
        for x, y in aligned:
            if x and y:
                print x[0], '\t', y[0]
            elif x:
                print x[0]
            elif y:
                print '\t', y[0]
    else:
        for x in aligned:
            print x
    
def showLines(date, dataownercode):
    cur.execute("SELECT lineplanningnumber, transporttype, linepublicnumber, linename FROM line WHERE dataownercode = %s", (dataownercode,))
    lines = cur.fetchall()

    for lineplanningnumber, transporttype, linepublicnumber, linename in lines:
        aligned = alignJourneyPatterns(date.today(), 'HTM', lineplanningnumber)

        print transporttype, linepublicnumber, '-', linename
        if aligned is None:
            print 'No pattern'
        else:
            printAligned(aligned)

showLines(date.today(), 'HTM')


# aligned = alignJourneyPatterns(date.today(), 'ARR', '16001')
