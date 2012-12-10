#!/usr/bin/env python2

import psycopg2
from datetime import date

conn = psycopg2.connect("dbname=kv78turbo")
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

    #for x in patterns:
    #    print x[0:3], x[3:6]

    order = 0;

    final = {}
    todo = {}
    output = []

    last_two = None
    for pattern in patterns:
        order += 1

        if pattern[0] and pattern[3]:
            final[order] = ([pattern[0:3], pattern[3:6]])
            if last_two is None and order > 1:
                last_two = int(pattern[4] - 1)
                for y in range(1, order):
                    final[order - y][1] = (last_two + y)
            else: 
                if last_two is not None and int(pattern[4]) > last_two:
                    y = 1
                    while type(final[order - y][1]) is int and final[order - y][1] <= pattern[4]:
                        final[order - y][1] = None
                        y += 1

                last_two = int(pattern[4] - 1)

        elif pattern[0]:
            final[order] = ([pattern[0:3], last_two])
            if last_two is not None:
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

    # There is a chance that the join resulted in multiple entries on the same stoparea
    # We are going to prune these entries now.

    #for x in final.values():
    #    print x[0], x[1]

    last_key = None
    last_one = None
    last_two = None
    for key, x in final.items():
        if x[0] is not None:
            this_one = x[0][1]
            if last_one is not None:
                if last_one == this_one:
                    if last_key in final:
                        # print last_two, x[1][1]
                        if last_two is not None and final[last_key][1] is not None and final[last_key][1][1] > x[1][1]:
                            redo = final.pop(key)[1]
                        else:
                            redo = final.pop(last_key)[1]
                        if redo is not None:
                            todo[redo[1]] = redo
                    else:
                        final.pop(key)
    
        if key in final and x[1] is not None:
            if type(x[1]) is int:
                final[key][1] = None
            else:
                this_two = x[1][1]
                if last_two is not None:
                    if last_two == this_two:
                        final[key][1] = None
                    elif last_two == 1:
                        todo[this_two] = x[1]
                        final[key][1] = None
                        this_two = 1
                    elif last_two < this_two:
                        todo[this_two] = x[1]
                        final[key][1] = None
                        this_two = last_two

                last_two = this_two
   
        last_key = key
        last_one = this_one 
    #print '-'
    #
    #for x in final.values():
    #    print x[0], x[1]


    # first = sorted(todo.keys(), reverse=True)

    remove = set([])
    for x in final.values():
        if x[1] is not None:
            remove.add(x[1][1])

    #print todo.keys()
    #print remove
    first = sorted(list(set(todo.keys()) - remove), reverse=True)
    last_two = None
    for x in final.values():
        while len(first) > 0:
            if (type(x[1]) is int and x[1] < first[0]) or (x[1] is not None and x[1][1] < first[0]):
                item = first.pop(0)

                if len(output) > 1 and output[-1][1] is None:
                    output[-1] = (output[-1][0], todo.pop(item))
                else:
                    output.append((None, todo.pop(item)))

            else:
                break

        if len(first) > 0 and len(output) > 0 and x[1] is None and output[-1][1] is not None and (output[-1][1][1] - 1) == first[0]:
            item = first.pop(0)
            output.append((x[0], todo.pop(item)))

        elif len(output) > 1 and x[1] is None and output[-1][0] is None:
            output[-1] = (x[0], output[-1][1])

        elif type(x[1]) is int and x[1] in first:
            output.append((x[0], todo.pop(x[1])))
            last_one = x[1]

        elif type(x[1]) is int:
            output.append((x[0], None))

        else:
            output.append((x[0], x[1]))

    while len(first) > 0:
        item = first.pop(0)
        output.append((None, todo.pop(item)))

    if len(first) > 0:
        print first
        printAligned(output)
        sys.exit()

    return output

def printAligned(aligned):
    maxlen = 4
    if len(aligned[0]) == 2:
        for x, y in aligned:
            if x and y:
                maxlen = max(len(x[0]), maxlen)
                print x[1], '\t', x[0], '\t', y[0], y[1]
            elif x:
                maxlen = max(len(x[0]), maxlen)
                print x[1], '\t', x[0]
            elif y:
                
                print ''.join([' ']*maxlen), '\t', '\t', y[0], y[1]
    else:
        for x in aligned:
            print x
 
def printAligned2(aligned):
    maxlen = 4
    if len(aligned[0]) == 2:
        for x, y in aligned:
            if x and y:
                maxlen = max(len(x[0]), maxlen)
                print x[1], x[2], y[2], y[1]
            elif x:
                maxlen = max(len(x[0]), maxlen)
                print x[1], x[2]
            elif y:
                
                print ''.join([' ']*maxlen), '\t', '\t', y[2], y[1]
    else:
        for x in aligned:
            print x

def html(dataownercode, aligned):
    cur.execute("SELECT userstopcode, timingpointname FROM usertimingpoint AS u, timingpoint AS t WHERE u.dataownercode = %s AND u.timingpointdataownercode = t.dataownercode AND u.timingpointcode = t.timingpointcode;", (dataownercode,))
    stops = {}
    for x in cur.fetchall():
        stops[x[0]] = x[1]

    if len(aligned[0]) == 2:
        output = '<table class="lijn"><tr><th class="left"><button class="btn btn-success btn-mini" onclick="selecteer(0);"><i class="icon-arrow-down icon-white"></i></th><th><button class="btn btn-success btn-mini" onclick="selecteer(2);"><i class="icon-resize-horizontal icon-white"></i></th><th class="right"><button class="btn btn-success btn-mini" onclick="selecteer(1);"><i class="icon-arrow-up icon-white"></i></th></tr>'
        for x, y in aligned:
            #if (x[2] is not None and x[2] == y[2]) or (x[0] == y[0]) or (stops[x[0]] == stops[y[0]]):
            if x is not None and y is not None:
                output += '<tr><td class="left"><button type="button" data-toggle="button" class-toggle="btn-success" class="btn btn-primary btn-mini" id="%(userstopcode1)s">%(timingpointname1)s</button></td><td><button class="btn btn-success btn-mini" onclick="selecteerHaltes(this);"><i class="icon-resize-horizontal icon-white"></i></td><td class="right"><button type="button" data-toggle="button" class-toggle="btn-success" class="btn btn-primary btn-mini" id="%(userstopcode2)s">%(timingpointname2)s</button></td></tr>\n'%{'dataownercode': dataownercode, 'userstopcode1': x[0], 'timingpointname1': stops[x[0]], 'userstopcode2': y[0], 'timingpointname2': stops[y[0]]}
            elif x is not None:
                output += '<tr><td class="left"><button type="button" data-toggle="button" class-toggle="btn-success" class="btn btn-primary btn-mini" id="%(userstopcode1)s">%(timingpointname1)s</button></td><td></td><td></td></tr>\n'%{'dataownercode': dataownercode, 'userstopcode1': x[0], 'timingpointname1': stops[x[0]]}
                
            elif y is not None:
                output += '<tr><td></td><td></td><td class="right"><button type="button" data-toggle="button" class-toggle="btn-success" class="btn btn-primary btn-mini" id="%(userstopcode2)s">%(timingpointname2)s</button></td></tr>\n'%{'dataownercode': dataownercode, 'userstopcode2': y[0], 'timingpointname2': stops[y[0]]}
        output += '</table>'

        return output
    else:
        return '<table class="lijn"><tr><th class="left"><button class="btn btn-success btn-mini" onclick="selecteer(0);"><i class="icon-arrow-down icon-white"></i></th></tr>'+''.join(['<tr><td class="left"><button type="button" data-toggle="button" class-toggle="btn-success" class="btn btn-primary btn-mini" id="%s_%s">%s</button></td></tr>\n'%(dataownercode, x, stops[x]) for x in aligned])+'</table>'


def getLines(today, dataownercode):
    output = {}
    cur.execute("SELECT lineplanningnumber, transporttype, linepublicnumber, linename FROM line WHERE dataownercode = %s", (dataownercode,))
    lines = cur.fetchall()

    for lineplanningnumber, transporttype, linepublicnumber, linename in lines:
        aligned = alignJourneyPatterns(today, dataownercode, lineplanningnumber)
        if aligned is not None:
            output[lineplanningnumber] = {'transporttype': transporttype, 'lineplanningnumber': lineplanningnumber, 'linepublicnumber': linepublicnumber, 'linename': linename, 'aligned': html(dataownercode, aligned)}

    return output

def showLines(today, dataownercode):
    cur.execute("SELECT lineplanningnumber, transporttype, linepublicnumber, linename FROM line WHERE dataownercode = %s and lineplanningnumber = '6'", (dataownercode,))
    lines = cur.fetchall()

    for lineplanningnumber, transporttype, linepublicnumber, linename in lines:
            print transporttype, linepublicnumber, '-', linename, lineplanningnumber
            aligned = alignJourneyPatterns(today, dataownercode, lineplanningnumber)

            if aligned is None:
                print 'No pattern'
            else:
                print html(dataownercode, aligned)

#showLines(date.today(), 'HTM')
#showLines(date.today(), 'ARR')
#showLines(date.today(), 'CXX')
#showLines(date.today(), 'VTN')
#showLines(date.today(), 'GVB')
